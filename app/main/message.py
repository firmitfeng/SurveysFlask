# -*- coding: utf-8 -*-
import os
import json
import datetime
from functools import wraps
from flask import render_template, session, redirect, url_for, current_app, \
    abort, flash, request, make_response, g
from flask_login import login_required, login_user, logout_user, current_user
from wtforms import HiddenField, StringField, BooleanField
from werkzeug import secure_filename
from utils.libserialnum import encodeSerialNum
from utils.libimage import resizeImg, Horizontal, Vertical, clipImg, clipReszImg
import pypinyin
from .. import db, csrf
from . import main
from app.models import SurveyPernission, SurveyStatus, SurveyPageType, \
        RelationType, OwnerType, \
        Role, User, UserMeta, \
        Survey, SurveyMeta, SurveyPage, SurveyResult, \
        Relation, Distribute, Message, MesgType
from sqlalchemy import and_
from forms import MessageForm, ReplyMessageForm


def getDayBeforeN(days=30):
    return datetime.date.today() - datetime.timedelta(days=days)


@main.route('/list-messages/', defaults={'path': 'in'})
@main.route('/list-messages/<path:path>', methods=['GET'])
@login_required
def listMessage(path):
    page = request.args.get('page', 1, type=int)
    if path == 'in':
        pagination = Message.query\
                    .filter(Message.receiver_id==current_user.id, Message.receiver_deled==0)\
                    .order_by(Message.ctime.desc())\
                    .paginate(page, per_page=current_app.config['ENTRIES_PER_PAGE'], \
                            error_out=False)
        template = 'main/list_message_inbox.html'
    elif path == 'out':
        pagination = Message.query\
                    .filter(Message.sender_id==current_user.id, Message.sender_deled==0)\
                    .order_by(Message.ctime.desc())\
                    .paginate(page, per_page=current_app.config['ENTRIES_PER_PAGE'], \
                            error_out=False)
        template = 'main/list_message_outbox.html'
    elif path == 'del':
        pagination = Message.query\
                    .filter(and_(Message.sender_id==current_user.id, Message.sender_deled!=0) |\
                            and_(Message.receiver_id==current_user.id, Message.receiver_deled!=0))\
                    .filter(Message.ctime > getDayBeforeN())\
                    .order_by(Message.ctime.desc())\
                    .paginate(page, per_page=current_app.config['ENTRIES_PER_PAGE'], \
                            error_out=False)
        template = 'main/list_message_delbox.html'

    messages = pagination.items
    return render_template(template,
                            messages=messages,
                            pagination=pagination,
                            pagetitle=u'查看消息',
                            path=path,
                            mesgManage='active'
                            )


@main.route('/read-message/<string:serial_num>.html', methods=["GET", 'POST'])
@login_required
def readMessage(serial_num):
    mesg = Message.query.filter_by(serial_num=serial_num).first_or_404()
    if mesg.receiver_id != current_user.id \
            and mesg.sender_id != current_user.id \
            and not current_user.is_administrator():
        return abort(404)

    form = None
    if mesg.receiver_id == current_user.id and mesg.type != MesgType.SYSTEM :
        if not mesg.is_read:
            mesg.is_read = datetime.datetime.now()
            db.session.add(mesg)
            db.session.commit()

        form = ReplyMessageForm()
        form.to_user.choices = [(mesg.sender_id, mesg.sender.name)]
        form.to_user.data = mesg.sender_id
        form.mesg_id.data = mesg.id
        if form.validate_on_submit():
            if int(form.mesg_id.data) != mesg.id:
                flash(u'发送失败')
                return redirect(url_for('main.listMessage'))

            re_mesg = Message(
                            subject = form.subject.data,
                            content = form.content.data,
                            sender_id = current_user.id,
                            receiver_id = form.to_user.data,
                            root = mesg.root,
                            parent = mesg
                            )
            re_mesg.type = MesgType.USER
            db.session.add(re_mesg)
            db.session.commit()
            flash(u'发送成功')
            return redirect(url_for('main.listMessage'))

        form.subject.data = u'Re: {}'.format(mesg.subject)
    
    return render_template('main/read_mesg.html',
                            message=mesg,
                            form=form,
                            pagetitle=u'查看消息',
                            prev=request.referrer,
                            mesgManage='active'
                            )



@main.route('/send-message/', methods=["GET", "POST"])
@login_required
def sendMessage():
    form = MessageForm()
    if not current_user.is_administrator():
        to_users = [(u.lower.id, u.lower.name)
                for u in current_user.lower.all()]
        to_users.extend([(u.upper.id, u.upper.name) 
                for u in current_user.upper.all()])
    else:
        to_users = [(u.id, u.name) 
                for u in User.query.filter(User.id!=current_user.id).all()]

    form.to_user.choices = to_users
    if form.validate_on_submit():
        mesg = Message(
                        subject = form.subject.data,
                        content = form.content.data,
                        sender_id = current_user.id,
                        receiver_id = form.to_user.data
                        )
        mesg.root = mesg
        if current_user.is_administrator():
            mesg.type = MesgType.SYSTEM
        else:
            mesg.type = MesgType.USER
        db.session.add(mesg)
        db.session.commit()
        flash(u'发送成功')
        return redirect(url_for('main.listMessage'))

    return render_template('main/send_mesg.html',
                            pagetitle=u'发送消息',
                            mesgManage='active',
                            form=form)


#@main.route('/reply-message/<string:mesg_id>.html', methods=["GET", "POST"])
#@login_required
#def replyMessage(mesg_id):
#    return "REPLY MESG"


@main.route('/del-message/<string:serial_num>.html', methods=["GET", 'POST'])
@login_required
def delMessage(serial_num):
    mesg = Message.query.filter_by(serial_num=serial_num).first_or_404()
    if mesg.receiver_id == current_user.id:
        mesg.receiver_deled = datetime.datetime.now()
    elif mesg.sender_id == current_user.id:
        mesg.sender_deled = datetime.datetime.now()
    elif current_user.is_administrator():
        return redirect('manage.index')
    else:
        flash(u'操作失败')
        return redirect(request.referrer)

    db.session.add(mesg)
    db.session.commit()

    flash(u'操作成功')
    return redirect(request.referrer)


@main.route('/restore-message/<string:serial_num>.html', methods=["GET"])
@login_required
def restoreMessage(serial_num):
    mesg = Message.query.filter_by(serial_num=serial_num).first_or_404()
    if mesg.receiver_id == current_user.id:
        mesg.receiver_deled = 0
    elif mesg.sender_id == current_user.id:
        mesg.sender_deled = 0
    elif current_user.is_administrator():
        return redirect('manage.index')
    else:
        flash(u'操作失败')
        return redirect(request.referrer)

    db.session.add(mesg)
    db.session.commit()

    flash(u'操作成功')
    return redirect(request.referrer)


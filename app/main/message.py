# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime
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
from forms import MessageForm


@main.route('/list-messages', methods=['GET'])
@login_required
def listMessage():
    page = request.args.get('page', 1, type=int)
    pagination = Message.query\
                    .filter((Message.sender_id==current_user.id and Message.sender_deled!=0) | \
                            (Message.receiver_id==current_user.id and  Message.receiver_deled!=0))\
                    .order_by(Message.ctime.desc())\
                    .paginate(page, per_page=current_app.config['ENTRIES_PER_PAGE'], \
                            error_out=False)
    messages = pagination.items
    return render_template('main/list_message.html',
                            messages=messages,
                            pagination=pagination,
                            pagetitle=u'查看消息',
                            )


@main.route('/read-message/<string:mesg_id>.html', methods=["GET"])
@login_required
def readMessage(mesg_id):
    return "READ MESG"


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
                            form=form)


@main.route('/reply-message/<string:mesg_id>.html', methods=["GET", "POST"])
@login_required
def replyMessage(mesg_id):
    return "REPLY MESG"


@main.route('/del-message/<string:mesg_id>.html', methods=["GET"])
@login_required
def delMessage(mesg_id):
    return "DEL MESG"

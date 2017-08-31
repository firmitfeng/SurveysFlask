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
from . import manage
from app.models import SurveyPernission, SurveyStatus, SurveyPageType, \
        RelationType, OwnerType, \
        Role, User, UserMeta, \
        Survey, SurveyMeta, SurveyPage, SurveyResult, \
        Relation, Distribute, Message, MesgType
from sqlalchemy import and_


@manage.route('/list-messages/', defaults={'path': ''})
@manage.route('/list-messages/<path:path>', methods=['GET'])
@login_required
def listMessage(path):
    if not current_user.is_administrator():
        return redirect(url_for('main.listMessage'))
    page = request.args.get('page', 1, type=int)
    if path == 'out':
        pagination = Message.query\
                    .filter(Message.sender_id==current_user.id, Message.sender_deled==0)\
                    .order_by(Message.ctime.desc())\
                    .paginate(page, per_page=current_app.config['ENTRIES_PER_PAGE'], \
                            error_out=False)
        template = 'manage/list_message_outbox.html'
    else:
        pagination = Message.query\
                    .order_by(Message.ctime.desc())\
                    .paginate(page, per_page=current_app.config['ENTRIES_PER_PAGE'], \
                            error_out=False)
        template = 'manage/list_message_all.html'

    messages = pagination.items
    return render_template(template,
                            messages=messages,
                            pagination=pagination,
                            pagetitle=u'查看消息',
                            path=path,
                            mesgManage='active'
                            )


@manage.route('/del-message/<string:serial_num>.html', methods=["GET", 'POST'])
@login_required
def delMessage(serial_num):
    if not current_user.is_administrator():
        return redirect('main.listMessage')
    mesg = Message.query.filter_by(serial_num=serial_num).first_or_404()

    db.session.delete(mesg)
    db.session.commit()

    flash(u'操作成功')
    return redirect(request.referrer)


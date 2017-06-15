# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime
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
        Relation, Distribute
from forms import ChangePasswordForm




@manage.route('/')
@login_required
def index():
    return render_template('manage/index.html')


@manage.route('/change-passwd', methods=["GET", "POST"])
@login_required
def ChangePasswd():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_passwd.data)\
                and form.re_passwd.data == form.new_passwd.data:
            current_user.password = form.new_passwd.data
            user_meta = UserMeta(meta_key='change_password',
                                 meta_value=json.dumps({'username':current_user.name}),
                                 owner = current_user
                                )
            db.session.add(current_user)
            db.session.add(user_meta)
            db.session.commit()
            logout_user()
            flash(u'修改成功，请重新登录')
            return redirect(url_for('manage.index'))
        else:
            flash(u'密码错误')
    return render_template('manage/change_passwd.html',
                            pagetitle=u'修改密码',
                            form=form, userInfo='active')



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
from . import main
from app.models import SurveyPernission, SurveyStatus, SurveyPageType, \
        RelationType, OwnerType, \
        Role, User, UserMeta, \
        Survey, SurveyMeta, SurveyPage, SurveyResult, \
        Relation, Distribute, Message, MesgType
from forms import LoginForm, RegForm, ChangePasswordForm



@main.route('/')
@login_required
def index():
    if current_user.role.name != 'visitor':
        return redirect(url_for('manage.index'))
    return render_template('main/index.html')


@main.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            user.ping()
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'用户名或密码错误')
    return render_template('main/login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    # flash(u'您已经退出')
    return redirect(url_for('main.index'))


@main.route('/reg', methods=["GET", "POST"])
def register():
    form = RegForm()
    if form.validate_on_submit():
        if form.password.data == form.re_passwd.data and\
                len(form.password.data) > 7:
            user = User(
                        name=form.name.data,
                        password=form.password.data,
                        email=form.email.data
                        )
            db.session.add(user)
            db.session.commit()
            flash(u'操作成功')
            return redirect(url_for('main.index'))
        else:
            flash(u'密码过短或两次输入不同')
    return render_template('main/reg.html', form=form)


@main.route('/change-passwd', methods=["GET", "POST"])
@login_required
def ChangePasswd():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_passwd.data)\
                and form.re_passwd.data == form.new_passwd.data:
            current_user.password = form.new_passwd.data
            user_meta = UserMeta(meta_key='change_password',
                                 meta_value=json.dumps({'username':current_user.name}),
                                 user = current_user
                                )
            db.session.add(current_user)
            db.session.add(user_meta)
            db.session.commit()
            logout_user()
            flash(u'修改成功，请重新登录')
            return redirect(url_for('main.index'))
        else:
            flash(u'密码错误')
    return render_template('main/change_passwd.html',
                            pagetitle=u'修改密码',
                            form=form, userInfo='active')


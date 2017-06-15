# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime
import random
import hashlib
from flask import render_template, session, redirect, url_for, current_app, \
        abort, flash, request, make_response, g
from flask_login import login_required, login_user, logout_user, current_user
from wtforms import HiddenField, StringField, BooleanField, RadioField, \
        TextAreaField, SubmitField
from wtforms.validators import DataRequired
from werkzeug import secure_filename
from utils.libserialnum import encodeSerialNum
from utils.libimage import resizeImg, Horizontal, Vertical, clipImg, clipReszImg
from utils.libform import MultiCheckboxField
import pypinyin
import yaml
from .. import db, csrf
from . import manage
from app.models import SurveyPernission, SurveyStatus, SurveyPageType, \
        RelationType, OwnerType, \
        Role, User, UserMeta, \
        Survey, SurveyMeta, SurveyPage, SurveyResult, \
        Relation, Distribute
from forms import addUserForm, editUserForm


@manage.route('/list-user', methods=["GET"])
@login_required
def listUser():
    page = request.args.get('page', 1, type=int)
    if current_user.is_administrator():
        pagination = User.query.order_by(User.id.asc())\
                        .paginate(page, per_page=current_app.config['ENTRIES_PER_PAGE'],
                                 error_out=False)
        users = pagination.items
    else:
        pagination = current_user.lower\
                        .order_by(User.id.asc())\
                        .paginate(page, per_page=current_app.config['ENTRIES_PER_PAGE'],
                                 error_out=False)
        users = (item.lower for item in pagination.items)

    return render_template('manage/list_user.html',
                           users=users,
                           pagination=pagination,
                           pagetitle=u'用户列表',
                           userManage='active'
                          )


@manage.route('/add-user', methods=["GET", "POST"])
@login_required
def addUser():
    form = addUserForm()
    if form.validate_on_submit():
        if form.password.data == form.re_passwd.data and\
                len(form.password.data) > 7:
            user = User(
                        name=form.name.data,
                        password=form.password.data,
                        email=form.email.data,
                        role=form.role.data
                        )
            user_meta = UserMeta(
                                meta_key='add_user',
                                meta_value=json.dumps({
                                                    'name': user.name,
                                                    'role': user.role.name,
                                                    'operator_id': current_user.id
                                                  }),
                                user=user
                                )

            db.session.add(user)
            db.session.add(user_meta)
            db.session.commit()

            flash(u'操作成功')
            return redirect(url_for('manage.listUser'))
        else:
            flash(u'密码过短或两次输入不同')
    return render_template('manage/add_user.html',
                           form=form,
                           pagetitle=u'添加用户',
                           userManage='active'
                          )


@manage.route('/edit-user/<int:user_id>', methods=["GET", "POST"])
@login_required
def editUser(user_id):
    if not current_user.is_administrator():
        flash(u'权限不足')
        return redirect(url_for('manage.listUser'))
    user = User.query.filter_by(id=user_id).first_or_404()
    form = editUserForm()

    if form.validate_on_submit():
        if int(form.user_id.data) != user_id:
            flash(u'权限不足')
            return redirect(url_for('manage.listUser'))

        if form.password.data:
            if form.password.data == form.re_passwd.data and\
                    len(form.password.data) > 7:
                user.password = form.password.data
            else:
                flash(u'密码过短或两次输入不同')
                return redirect(url_for('manage.editUser', user_id=user_id))

        user.role = form.role.data
        user.email = form.email.data

        user_meta = UserMeta(
                             meta_key='change_user',
                             meta_value=json.dumps({
                                                    'name': user.name,
                                                    'role': user.role.name,
                                                    'operator': current_user.name
                                                  }),
                             user=user
                             )

        db.session.add(user)
        db.session.add(user_meta)
        db.session.commit()

        flash(u'操作成功')
        return redirect(url_for('manage.listUser'))
    else:
        form.name.data = user.name
        form.email.data = user.email
        form.role.data = user.role
        form.user_id.data = user.id    

    return render_template('manage/edit_user.html',
                           form=form,
                           pagetitle=u'编辑用户',
                           userManage='active'
                          )


@manage.route('/del-user/<int:user_id>', methods=["GET", "POST"])
@login_required
def delUser(user_id):
    if not current_user.is_administrator():
        flash(u'权限不足')
        return redirect(url_for('manage.listUser'))
    user = User.query.filter_by(id=user_id).first_or_404()
    user_meta = UserMeta(
                            meta_key='delete_user',
                            meta_value=json.dumps({
                                                    'name': user.name,
                                                    'email': user.email,
                                                    'role': user.role.name,
                                                    'operator': current_user.name
                                                  })
                            )
    db.session.delete(user)
    db.session.add(user_meta)
    db.session.commit()
    flash(u'操作成功')
    return redirect(url_for('manage.listUser'))


@manage.route('/distribute-user/',  methods=["GET", "POST"])
@login_required
def distributeUser():
    return "distributeUser"

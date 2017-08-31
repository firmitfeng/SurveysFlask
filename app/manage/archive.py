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
        Relation, Distribute, Archive
from forms import addArchiveForm, editArchiveForm


@manage.route('/list-archives/<int:user_id>', methods=['GET'])
@login_required
def listArchives(user_id):
    page = request.args.get('page', 1, type=int)
    target = User.query.filter_by(id=user_id).first_or_404()
    if current_user.role.name == 'psycho':
        pagination = Archive.query\
                        .filter_by(author_id=current_user.id)\
                        .filter_by(target_id=user_id)\
                        .order_by(Archive.ctime.desc())\
                        .paginate(page, per_page=current_app.config['ENTRIES_PER_PAGE'], \
                            error_out=False)
    elif current_user.role.name == 'supervisor' \
            or current_user.is_administrator():
        pagination = Archive.query\
                        .filter((Archive.author_id==target.id) | \
                                (Archive.target_id==target.id)) \
                        .order_by(Archive.ctime.desc())\
                        .paginate(page, per_page=current_app.config['ENTRIES_PER_PAGE'], \
                            error_out=False)
    else:
        flash(u'权限不足')
        return redirect(url_for('manage.listArchives', user_id=user_id))

    archives = pagination.items
    return render_template('manage/list_archives.html',
                            archives=archives,
                            pagination=pagination,
                            user_id=user_id,
                            pagetitle=u'{}的记录一览'.format(target.name),
                            userManage='active'
                            )


@manage.route('/display-archive/<int:archive_id>', methods=['GET'])
@login_required
def displayArchive(archive_id):
    archive = Archive.query.filter_by(id=archive_id).first_or_404()
    if current_user.role.name == 'visitor':
        return redirect(url_for('main.index'))
    elif current_user.role.name == 'psycho' \
            and archive.author_id != current_user.id:
        flash(u'权限不足')
        return redirect(url_for('manage.listArchives'))
    elif current_user.role.name == 'supervisor':
        lower = current_user.lower.filter_by(lower_id=archive.author_id).first()
        if archive.author_id != current_user.id and lower is None:
            flash(u'权限不足')
            return redirect(url_for('manage.listUser'))
    return render_template('manage/disp_archive.html',
                            archive=archive,
                            userManage='active'
                            )


@manage.route('/add-archive/<int:user_id>', methods=['GET', 'POST'])
@login_required
def addArchive(user_id):
    form = addArchiveForm()
    target = User.query.filter_by(id=user_id).first_or_404()
    form.to_user_id.data = user_id
    if form.validate_on_submit():
        if int(form.to_user_id.data) != user_id :
            flash(u'权限不足')
            return redirect(url_for('manage.listArchives', user_id=user_id))
        
        if form.title.data == '':
            name_py = pypinyin.slug(target.name)
            name_py = name_py.replace(u' ', u'-')
            title = '{} {}'.format(
                                datetime.now().strftime('%Y-%m-%d-%H-%M'), 
                                name_py)
        else:
            title = form.title.data

        archive = Archive(
                        title=title,
                        content=form.content.data,
                        keywords=form.keywords.data,
                        target=target,
                        author=current_user
                        )
        if current_user.role.name == 'psycho':
            archive.type = RelationType.VISIT
        elif current_user.role.name == 'supervisor':
            archive.type = RelationType.SUPERVISE

        if current_user.is_administrator():
            archive.type = 'ADMIN'

        db.session.add(archive)
        db.session.commit()

        flash(u'操作成功')
        return redirect(url_for('manage.listArchives', user_id=user_id))
    return render_template('manage/add_archive.html',
                           form=form,
                           pagetitle=u'添加记录',
                           userManage='active'
                          )


@manage.route('/edit-archive/<int:user_id>/<int:archive_id>', methods=['GET', 'POST'])
@login_required
def editArchive(user_id, archive_id):
    archive = Archive.query.filter_by(id=archive_id).first_or_404()
    if not current_user.is_administrator() and \
            archive.author != current_user:
        flash(u'权限不足')
        return redirect(url_for('manage.listArchives', user_id=user_id))
    form = editArchiveForm()

    if form.validate_on_submit():
        if form.title.data == '':
            name_py = pypinyin.slug(target.name)
            name_py = name_py.replace(u' ', u'-')
            title = '{} {}'.format(
                    datetime.now().strftime('%Y-%m-%d-%H-%M'), 
                    name_py)
        else:
            title = form.title.data

        archive.title=title
        archive.content=form.content.data
        archive.keywords=form.keywords.data

        db.session.add(archive)
        db.session.commit()
        flash(u'操作成功')
        return redirect(url_for('manage.listArchives', user_id=user_id))

    form.title.data = archive.title
    form.content.data = archive.content
    form.keywords.data = archive.keywords
    form.archive_id.data = archive_id
    form.to_user_id.data = archive.target_id

    return render_template('manage/edit_archive.html',
            form=form,
            pagetitle=u'编辑记录',
            userManage='active'
            )


@manage.route('/del-archive/<int:user_id>/<int:archive_id>', methods=['GET'])
@login_required
def delArchive(user_id, archive_id):
    if not current_user.is_administrator():
        flash(u'权限不足')
        return redirect(url_for('manage.listArchives', user_id=user_id))
    archive = Archive.query.filter_by(id=archive_id).first_or_404()
    db.session.delete(archive)
    db.session.commit()
    flash(u'操作成功')
    return redirect(url_for('manage.listArchives', user_id=user_id))


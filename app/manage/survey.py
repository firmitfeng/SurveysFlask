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
from utils.libform import MultiCheckboxField, LabelRadioField
import pypinyin
import yaml
from .. import db, csrf
from . import manage
from app.models import SurveyPernission, SurveyStatus, SurveyPageType, \
        RelationType, OwnerType, \
        Role, User, UserMeta, \
        Survey, SurveyMeta, SurveyPage, SurveyResult, \
        Relation, Distribute
from forms import SurveyBaseForm, addSurveyForm, editSurveyForm, distribSurveyForm


def loadYAML(y_str, key='pages'):
    return yaml.load(y_str)[key]


def getRandStr(s):
    return hashlib.md5(s).hexdigest()[:8].upper()

def buildSurveyForm(item_list):
    survey_page_attrs = {}
    i = 0
    for item in item_list:
        i += 1
        if 'id' not in item:
            item['id'] = 'q_{}_{}'.format(getRandStr(item['title']), i)
        if 'style' not in item:
            item['style'] = 'basic'
        if 'required' not in item:
            item['required'] = 1
        if item['type'] == 'radio':
            survey_page_attrs[item['id']] = LabelRadioField(item['title'], coerce=int,
                                                validators=[DataRequired()],
                                                choices=[tuple(v) for v in item['value'] ])
        elif item['type'] == 'check':
            survey_page_attrs[item['id']] = MultiCheckboxField(item['title'], coerce=int,
                                                validators=[DataRequired()],
                                                choices=[tuple(v) for v in item['value'] ])
        elif item['type'] == 'text':
            survey_page_attrs[item['id']] = TextAreaField(item['title'],
                                                widget=TextArea(),
                                                validators=[DataRequired()],
                                                render_kw={'class': 'text-body', 'rows': 20}
                                                )
        elif item['type'] == 'input':
            survey_page_attrs[item['id']] = StringField(item['title'],
                                                validators=[DataRequired()])
        else:
            survey_page_attrs[item['id']] = StringField(item['title'])
        
    MyForm = type('MyForm', (SurveyBaseForm,), survey_page_attrs)
    return MyForm() 


@manage.route('/preview-survey/<int:survey_id>', methods=["GET", "POST"])
@login_required
def previewSurvey(survey_id):
    survey = Survey.query.filter_by(id=survey_id).first_or_404()
    #survey_origin = survey.metas.filter_by(meta_key='survey_origin')\
    #                    .order_by(SurveyMeta.id.desc())\
    #                    .first().meta_value
    survey_pages = loadYAML(survey.content_origin)
    preview = []
    for page in survey_pages:
        form = buildSurveyForm(page['items'])
        preview.append(render_template('manage/survey_page.html',
                                        form=form, info=page['info']
                                      ))
    return '<hr>'.join(preview)


@manage.route('/list-survey', methods=["GET"])
@login_required
def listSurvey():
    page = request.args.get('page', 1, type=int)
    if current_user.is_administrator():
        pagination = Survey.query.filter(Survey.status != SurveyStatus.DELETE)\
                        .order_by(Survey.id.asc())\
                        .paginate(page, per_page=current_app.config['ENTRIES_PER_PAGE'],
                                 error_out=False)
        surveys = pagination.items
    else:
        pagination = current_user.own_surveys.filter(Survey.status != SurveyStatus.DELETE)\
                        .order_by(Survey.id.asc())\
                        .paginate(page, per_page=current_app.config['ENTRIES_PER_PAGE'],
                                 error_out=False)
        surveys = (item.survey for item in pagination.items)

    return render_template('manage/list_survey.html',
                           surveys=surveys,
                           pagination=pagination,
                           pagetitle=u'问卷列表',
                           surveyManage='active'
                          )


@manage.route('/add-survey', methods=["GET", "POST"])
@login_required
def addSurvey():
    form = addSurveyForm()
    if form.validate_on_submit():
        survey = Survey(
                        title=form.title.data,
                        description=form.describe.data,
                        content_origin=form.content.data,
                        dimension=form.dimension.data,
                        uptime=datetime.now(),
                        author=current_user
                        )
        if current_user.is_administrator():
            survey.status = SurveyStatus.PUB

        survey_origin = SurveyMeta(
                                   meta_key='survey_origin',
                                   meta_value=form.content.data,
                                   author_id=current_user.id,
                                   survey=survey
                                  )

        db.session.add(survey)
        db.session.add(survey_origin)
        db.session.add(Distribute(owner=current_user, 
                                  survey=survey, 
                                  type=OwnerType.OWNER))
        db.session.commit()

        flash(u'操作成功')
        return redirect(url_for('manage.listSurvey'))
    return render_template('manage/add_survey.html',
                           form=form,
                           pagetitle=u'添加问卷',
                           surveyManage='active'
                          )


@manage.route('/edit-survey/<int:survey_id>', methods=["GET", "POST"])
@login_required
def editSurvey(survey_id):
    survey = Survey.query.filter_by(id=survey_id).first_or_404()
    if not current_user.is_administrator() and \
        survey.author != current_user:
        flash(u'权限不足')
        return redirect(url_for('manage.listSurvey'))
#    survey_origin = survey.metas.filter_by(meta_key='survey_origin')\
#                        .order_by(SurveyMeta.id.desc())\
#                        .first().meta_value
    form = editSurveyForm()
    if form.validate_on_submit() and \
            survey_id == int(form.survey_id.data):
        survey.title = form.title.data
        survey.description = form.describe.data
        survey.content_origin = form.content.data
        survey.dimension = form.dimension.data
        survey.uptime = datetime.now()

        if current_user.is_administrator():
            survey.status = SurveyStatus.PUB

        survey_origin = SurveyMeta(
                                   meta_key='survey_origin',
                                   meta_value=form.content.data,
                                   author_id=current_user.id,
                                   survey=survey
                                  )

        db.session.add(survey)
        db.session.add(survey_origin)
        db.session.commit()

        flash(u'操作成功')
        return redirect(url_for('manage.listSurvey'))
    else:
        form.title.data = survey.title
        form.content.data = survey.content_origin
        form.dimension.data = survey.dimension
        form.describe.data = survey.description
        form.survey_id.data = survey.id    

    return render_template('manage/edit_survey.html',
                           form=form,
                           pagetitle=u'编辑问卷',
                           surveyManage='active'
                          )


@manage.route('/del-survey/<int:survey_id>', methods=["GET", "POST"])
@login_required
def delSurvey(survey_id):
    if not current_user.is_administrator():
        flash(u'权限不足')
        return redirect(url_for('manage.listSurvey'))
    survey = Survey.query.filter_by(id=survey_id).first_or_404()
    survey.status = SurveyStatus.DELETE
    survey_meta = SurveyMeta(
                            meta_key='delete_survey_user',
                            meta_value=current_user.name,
                            author_id=current_user.id,
                            survey=survey
                            )
    db.session.add(survey)
    db.session.add(survey_meta)
    db.session.commit()
    flash(u'操作成功')
    return redirect(url_for('manage.listSurvey'))


@manage.route('/distribute-survey/',  methods=["GET", "POST"])
@login_required
def distributeSurvey():
    user_id = request.args.get('user_id', 0, type=int)
    if not user_id:
        abort(404)

    user = User.query.filter_by(id=user_id).first_or_404()
    if user.role.name == 'visitor':
        dis_type = OwnerType.VISITOR
    elif user.role.name == 'psycho':
        dis_type = OwnerType.PSYCHO
    elif user.role.name == 'supervisor':
        dis_type = OwnerType.SUPER
    else:
        abort(500)

    form = distribSurveyForm()
    if current_user.is_administrator():
        surveys = Survey.query.filter(Survey.status != SurveyStatus.DELETE)\
                        .order_by(Survey.id.asc())\
                        .all()
    else:
        surveys = [own.survey for own in current_user.own_surveys\
                                    .filter(Survey.status != SurveyStatus.DELETE)\
                                    .order_by(Survey.id.asc()).all()]
    if not surveys:
        return u'没有可供分发的问卷'

    form.user_id = user_id
    form.surveys.choices = [(s.id, s.title) for s in surveys]

    if form.is_submitted():
        #删除指定用户所有的分配
        user.own_surveys.delete()
        db.session.commit()
        for survey_id in form.surveys.data:
            db.session.add(Distribute(
                                      user_id=user_id, 
                                      survey_id=survey_id, 
                                      type=dis_type))
        db.session.commit()
        flash(u'操作成功')
        return redirect(url_for('manage.listUser'))
    else:

        user_own = [str(own.survey.id) for own in user.own_surveys\
                                    .filter(Survey.status != SurveyStatus.DELETE)\
                                    .order_by(Survey.id.asc()).all()]
        return render_template('manage/list_discribute_surveys.html',
                                form=form,
                                user_own=user_own,
                                user_id=user_id
                                )

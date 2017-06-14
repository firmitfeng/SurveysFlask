# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app, \
        abort, flash, request, make_response, g
from flask_login import login_required, login_user, logout_user, current_user
from wtforms import HiddenField, StringField, BooleanField, RadioField, \
        TextAreaField, SubmitField
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
from forms import SurveyBaseForm, addSurveyForm


class LabelRadioField(RadioField):
    pass


@manage.route('/list-survey', methods=["GET"])
@login_required
def listSurvey():
    return 'listSurvey'


def buildSurveyForm(item_list):
    survey_page_attrs = {}
    for item in item_list:
        if item['type'] == 'radio':
            survey_page_attrs[item['id']] = LabelRadioField(item['title'],
                                                choices=[tuple(v) for v in item['value'] ])
        elif item['type'] == 'check':
            survey_page_attrs[item['id']] = MultiCheckboxField(item['title'],
                                                choices=[tuple(v) for v in item['value'] ])
        elif item['type'] == 'text':
            survey_page_attrs[item['id']] = TextAreaField(item['title'],
                                                widget=TextArea(),
                                                render_kw={'class': 'text-body', 'rows': 20}
                                                )
        elif item['type'] == 'input':
            survey_page_attrs[item['id']] = StringField(item['title'])

    return type('MyForm', (SurveyBaseForm,), survey_page_attrs)


@manage.route('/add-survey', methods=["GET", "POST"])
@login_required
def addSurvey():
    form = addSurveyForm()
    if form.validate_on_submit():
        survey = Survey(
                        title=form.title.data,
                        description=form.describe.data,
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
    return 'editSurvey'


@manage.route('/del-survey/<int:survey_id>', methods=["GET", "POST"])
@login_required
def delSurvey(survey_id):
    return 'delSurvey'


@manage.route('/distribute-survey/',  methods=["GET", "POST"])
@login_required
def distributeSurvey():
    return "distributeSurvey"

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
from forms import SurveyBaseForm, addSurveyForm



@manage.route('/list-survey', methods=["GET"])
@login_required
def listSurvey():
    return 'listSurvey'


@manage.route('/add-survey', methods=["GET", "POST"])
@login_required
def addSurvey():
    form = addSurveyForm()
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

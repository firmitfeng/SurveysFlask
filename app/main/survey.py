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
from . import main
from app.models import SurveyPernission, SurveyStatus, SurveyPageType, \
        RelationType, OwnerType, \
        Role, User, UserMeta, \
        Survey, SurveyMeta, SurveyPage, SurveyResult, \
        Relation, Distribute
from app.manage.survey import loadYAML, buildSurveyForm, computeDimenScore


@main.route('/list-survey', methods=["GET"])
@login_required
def listSurvey():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.own_surveys.filter(Survey.status != SurveyStatus.DELETE)\
                        .order_by(Survey.id.asc())\
                        .paginate(page, per_page=current_app.config['ENTRIES_PER_PAGE'],
                                  error_out=False)
    surveys = (item.survey for item in pagination.items)

    return render_template('main/list_survey.html',
                           surveys=surveys,
                           pagination=pagination,
                           pagetitle=u'我的问卷',
                           surveyManage='active'
                          )


def getResultfromForm(form, sub_survey):
    result = {}
    for item in sub_survey:
        if hasattr(form, item['id']):
            result[item['id']] = getattr(form, item['id']).data
    return result

    
@main.route('/survey/<string:slug>.html' , methods=["GET", "POST"])
@login_required
def fillSurvey(slug):
    survey = Survey.query.filter_by(slug=slug).first_or_404()
    survey_pages = loadYAML(survey.content_origin)
    current_page = request.args.get('p', 0, type=int)
    current_sub_survey = survey_pages[current_page]
    page_count = len(survey_pages) - 1

    form = buildSurveyForm(current_sub_survey['items'])

    if form.validate_on_submit():
        if survey.id != int(form.survey_id.data):
            flash(u'填写完成，感谢您的参与')
            return redirect(url_for('main.index'))

        result = SurveyResult.query\
                    .filter_by(user=current_user)\
                    .filter_by(survey=survey)\
                    .first()
        if not result:
            result = SurveyResult(user=current_user, survey=survey)

        if current_page is 0:
            result.result = '{}'

        temp = dict(json.loads(result.result))
        temp.update(getResultfromForm(form, current_sub_survey['items']))
        result.result = json.dumps(temp)
        result.uptime = datetime.now()

        #页数加1，重新生成form
        current_page += 1
        if current_page > page_count:
            dimen_score = computeDimenScore(temp, yaml.load(survey.dimension))
            result.result = json.dumps({'origin':temp, 'dimen':dimen_score})
            db.session.add(result)
            db.session.commit()

            flash(u'填写完成，感谢您的参与')
            return redirect(url_for('main.index'))
        else:
            current_sub_survey = survey_pages[current_page]
            form = buildSurveyForm(current_sub_survey['items'])

            db.session.add(result)
            db.session.add(UserMeta(meta_key='fill_survey',
                                meta_value='survey: {} {} page: {}'\
                                        .format(survey.id, survey.title, current_page),
                                user=current_user
                                ))
            db.session.commit()

    form.survey_id.data = survey.id
    form.p.data = current_page
    if 'style' in current_sub_survey:
        s_style = current_sub_survey['style']
    else:
        s_style = 'survey'
    return render_template('main/survey.html',
                           form=form,
                           survey=survey,
                           info=current_sub_survey['info'],
                           style=s_style,
                           pc=page_count, pn=current_page
                          ) 

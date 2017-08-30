# -*- coding: utf-8 -*-
from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, \
        RadioField, TextAreaField, SubmitField, SelectField, HiddenField, \
        DateField, DateTimeField
from wtforms.widgets import TextArea, CheckboxInput, ListWidget, RadioInput
from wtforms.validators import InputRequired, Length, Email, Regexp, EqualTo, DataRequired
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from datetime import datetime
from app.models import Role
from utils.libform import MultiCheckboxField, LabelRadioField


#class CheckboxSelectField(QuerySelectMultipleField):
class CheckboxSelectField(QuerySelectField):
    widget = ListWidget(prefix_label=False)
    #option_widget = CheckboxInput()
    option_widget = RadioInput()


def getRoles():
    return Role.query


class addUserForm(Form):
    name = StringField(u'用户名', validators=[DataRequired()],
                        render_kw={'placeholder': u'请输入用户名'})
    email = StringField(u'电子邮件', \
                validators=[DataRequired(), Length(1,100), Email()],
                render_kw={'placeholder': u'请输入电子邮件'})
    password = PasswordField(u'密码', \
                    validators=[DataRequired(), Length(8,32)],\
                    render_kw={'placeholder': u'请输入密码，长度8-32位'})
    re_passwd = PasswordField(u'重复密码', \
                    validators=[EqualTo('password', message='两次输入的密码不同')],\
                    render_kw={'placeholder': u'请再次输入密码'})
    role = QuerySelectField(u'角色', query_factory=getRoles,
                            get_pk=lambda r: r.id, get_label='name')

    submit = SubmitField(u'提交')


class editUserForm(addUserForm):
    password = PasswordField(u'密码', \
                    #validators=[Length(8,32)],\
                    render_kw={'placeholder': u'请输入密码，不修改请留空'})
    re_passwd = PasswordField(u'重复密码', \
                    validators=[EqualTo('password', message='两次输入的密码不同')],\
                    render_kw={'placeholder': u'请再次输入密码'})
    user_id = HiddenField(u'user_id')


class SurveyBaseForm(Form):
    @classmethod
    def append_field(cls, name, field):
        setattr(cls, name, field)
        return cls


class addSurveyForm(SurveyBaseForm):
    title = StringField(u'标题', validators=[DataRequired(), Length(1,350)],\
                        render_kw={'placeholder': u'请输入标题'})
    content = TextAreaField(u'内容', widget=TextArea(), \
                            render_kw={'class': 'text-body', 'rows': 20})
    dimension = TextAreaField(u'维度', widget=TextArea(), \
                            render_kw={'class': 'text-body', 'rows': 10})
    describe = StringField(u'说明')
    submit = SubmitField(u'提交')


class editSurveyForm(addSurveyForm):
    survey_id = HiddenField(u'survey_id')


class distribSurveyForm(Form):
    user_id = HiddenField(u'user_id')
    surveys = MultiCheckboxField(u'选择问卷', coerce=int, choices=[]) 


class distribPsychoForm(Form):
    user_id = HiddenField(u'user_id')
    uppers = LabelRadioField(u'选择咨询师', coerce=int, choices=[])


class distribSupervisorForm(Form):
    user_id = HiddenField(u'user_id')
    uppers = LabelRadioField(u'选择督导师', coerce=int, choices=[])


class addArchiveForm(Form):
    title = StringField(u'标题', render_kw={'placeholder': u'请输入标题'})
    content = TextAreaField(u'内容', widget=TextArea(), \
                            render_kw={'class': 'text-body', 'rows': 20})
    keywords = StringField(u'关键词', render_kw={'placeholder': u'请输入关键词'})

    to_user_id = HiddenField(u'to_user_id')
    submit = SubmitField(u'提交')


class editArchiveForm(addArchiveForm):
    archive_id = HiddenField(u'archive_id')

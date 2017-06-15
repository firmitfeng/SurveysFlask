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


#class CheckboxSelectField(QuerySelectMultipleField):
class CheckboxSelectField(QuerySelectField):
    widget = ListWidget(prefix_label=False)
    #option_widget = CheckboxInput()
    option_widget = RadioInput()


class PicRadioField(RadioField):
    pass


class LoginForm(Form):
    email = StringField(u'电子邮件', \
                validators=[DataRequired(), Length(1,100), Email()])
    password = PasswordField(u'密码', validators=[DataRequired()])
    remember_me = BooleanField(u'保持登录')
    submit = SubmitField(u'登录')


class ChangePasswordForm(Form):
    old_passwd = PasswordField(u'原始密码', validators=[DataRequired()],\
                    render_kw={'placeholder': u'请输入原始密码'})
    new_passwd = PasswordField(u'新的密码', \
                    validators=[DataRequired(), Length(8,32)],\
                    render_kw={'placeholder': u'请输入新的密码'})
    re_passwd = PasswordField(u'重复密码', \
                    validators=[EqualTo('new_passwd', message='两次输入的密码不同')],\
                    render_kw={'placeholder': u'请再次输入新的密码'})
    submit = SubmitField(u'提交')


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
    describe = StringField(u'说明')
    submit = SubmitField(u'提交')


class editSurveyForm(addSurveyForm):
    survey_id = HiddenField(u'survey_id')

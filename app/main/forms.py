# -*- coding: utf-8 -*-
from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, \
        RadioField, TextAreaField, SubmitField, SelectField, HiddenField, \
        DateField, DateTimeField, SelectMultipleField
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


class LoginForm(Form):
    email = StringField(u'电子邮件', \
                validators=[DataRequired(), Length(1,100), Email()])
    password = PasswordField(u'密码', validators=[DataRequired()])
    remember_me = BooleanField(u'保持登录')
#    submit = SubmitField(u'登录')


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


class RegForm(Form):
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

    submit = SubmitField(u'提交')


class SurveyBaseForm(Form):
    @classmethod
    def append_field(cls, name, field):
        setattr(cls, name, field)
        return cls


class MessageForm(Form):
    to_user = SelectField(u'收件人', coerce=int, choices=[])
    subject = StringField(u'主题', validators=[DataRequired()],
                            render_kw={'placeholder': u'请输入主题'})
    content = TextAreaField(u'内容', widget=TextArea(), \
                            render_kw={'class': 'text-body', 'rows': 20})
    submit = SubmitField(u'发送')


class ReplyMessageForm(MessageForm):
    mesg_id = HiddenField(u'mesg_id')

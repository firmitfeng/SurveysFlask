# -*- coding: utf-8 -*-
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin

from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
from flask import current_app, request
import bleach
import pypinyin
from . import db
from . import login_manager
from utils.libserialnum import encodeSerialNum, decodeSerialNum
from sqlalchemy.orm.collections import attribute_mapped_collection


class SurveyPernission:
    NONE = 0x0
    READ = 0x1
    CREATE = 0x2
    UPDATA = 0x4
    DELETE = 0x8
    ADMINISTRATOR = 0xF


class SurveyStatus:
    PUB = 0x8
    CHECK = 0x2
    DELETE = 0x0


class SurveyPageType:
    MASTERPAGE = 'master'
    SUBPAGE = 'sub'


class RelationType:
    VISIT = 'visitor_psycho'
    SUPERVISE = 'psycho_super'


class OwnerType:
    VISITOR = 'visitor'
    PSYCHO = 'psycho'
    SUPER = 'supervisor'
    OWNER = 'owner'


class MesgType:
    SYSTEM = 'system'
    USER = 'user'


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False)
    permissions = db.Column(db.Integer, default=SurveyPernission.NONE)
    users = db.relationship('User', backref='role', lazy="dynamic")

    @staticmethod
    def insert_role():
        roles = {
            'visitor': (SurveyPernission.READ, True),
            'psycho': (SurveyPernission.CREATE, False),
            'supervisor': (SurveyPernission.READ, False),
            'administrator': (-1, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class Relation(db.Model):
    ''' 定义用户之间的从属关系  '''
    __tablename__ = 'relations'
    #id = db.Column(db.Integer, primary_key=True)
    #被监管人的ID
    lower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    #管理员的ID
    upper_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    type = db.Column(db.String(64))
    ctime = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<upper id %r, lower id %r>' % \
                   (self.upper_id, self.lower_id)


class Distribute(db.Model):
    '''  定义用户和问卷之间的分配关系  '''
    __tablename__ = 'distribute'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), primary_key=True)
    type = db.Column(db.String(64))
    ctime = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<survey: {}, user: {}>'.format(self.survey_id, self.user_id)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True)
    email = db.Column(db.String(128), unique=True, index=True)
    #phone = db.Column(db.String(24))
    password_hash = db.Column(db.String(128))
    last_login_ip = db.Column(db.String(32))
    last_login_time = db.Column(db.DateTime, default=datetime.now())
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    upper = db.relationship('Relation', foreign_keys=[Relation.lower_id],
                            backref=db.backref('lower', lazy='joined'),
                            lazy='dynamic')

    lower = db.relationship('Relation', foreign_keys=[Relation.upper_id],
                            backref=db.backref('upper', lazy='joined'),
                            lazy='dynamic')
                            #cascade='all, delete-orphan'
                            #)

    own_surveys = db.relationship('Distribute', foreign_keys=[Distribute.user_id],
                              backref=db.backref('owner', lazy='joined'),
                              lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        #self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(-1)

    def ping(self):
        self.last_login_time = datetime.now()
        self.last_login_ip = request.remote_addr
        db.session.add(self)

    def __repr__(self):
        return '<User {}, {}>'.format(self.name, self.email)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class UserMeta(db.Model):
    __tablename__ = 'user_metas'
    id = db.Column(db.Integer, primary_key=True)
    meta_key = db.Column(db.String(250), index=True)
    meta_value = db.Column(db.Text)
    ctime = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User',
                            backref = db.backref('user_metas', lazy='dynamic')
                            )

    def __repr__(self):
        return '<UserMeta {}, {}>'.format(self.meta_key, self.meta_value)


class Survey(db.Model):
    __tablename__ = 'surveys'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    slug = db.Column(db.String(1000), index=True)
    description = db.Column(db.Text)
    content_origin = db.Column(db.Text)
    dimension = db.Column(db.Text)
    status = db.Column(db.Integer, default=SurveyStatus.CHECK)
    ctime = db.Column(db.DateTime, default=datetime.now())
    uptime = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User',
                            backref = db.backref('created_surveys', lazy='joined')
                            )

    owner = db.relationship('Distribute', foreign_keys=[Distribute.survey_id],
                            backref=db.backref('survey', lazy='joined'),
                            lazy='dynamic')

    @staticmethod
    def on_changed_title(target, value, oldvalue, initiator):
        value = "".join(value.split())
        target.slug = pypinyin.slug(value[:25])
        target.slug = target.slug.replace(u' ', u'-')

    def __repr__(self):
        return '<Survey {}>'.format(self.title)

db.event.listen(Survey.title, 'set', Survey.on_changed_title)


class SurveyMeta(db.Model):
    __tablename__ = 'survey_metas'
    id = db.Column(db.Integer, primary_key=True)
    meta_key = db.Column(db.String(250), index=True)
    meta_value = db.Column(db.Text)
    ctime = db.Column(db.DateTime, default=datetime.now())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'))

    survey = db.relationship('Survey',
                            backref = db.backref('metas', lazy='dynamic')
                            )

    def __repr__(self):
        return '<SurveyMeta {}: {}>'.format(self.survey_id, self.meta_key)


class SurveyPage(db.Model):
    __tablename__ = 'survey_pages'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32), default=SurveyPageType.MASTERPAGE)
    slug = db.Column(db.String(255), index=True)
    ordering = db.Column(db.Integer, default=0)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    ctime = db.Column(db.DateTime, default=datetime.now())
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'))

    survey = db.relationship('Survey',
                            backref = db.backref('survey_pages', lazy='dynamic')
                            )

    def __repr__(self):
        return '<SurveyPage {}: {}>'.format(self.survey_id, self.slug)


class SurveyResult(db.Model):
    __tablename__ = 'survey_results'
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.Text)
    ctime = db.Column(db.DateTime, default=datetime.now())
    uptime = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User',
                           backref = db.backref('results', lazy='dynamic')
                          )
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'))
    survey = db.relationship('Survey',
                            backref = db.backref('results', lazy='dynamic')
                            )

    def __repr__(self):
        return '<SurveyResult user: {} survey: {}>'.format(self.user_id, self.survey_id)


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(255))
    content = db.Column(db.Text)
    type = db.Column(db.String(64))
    is_read = db.Column(db.SmallInteger, default=0)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sender = db.relationship('User',
                            primaryjoin = "Message.sender_id == User.id",
                            backref=db.backref("message_sended", lazy='dynamic')
                            )
    receiver = db.relationship('User',
                              primaryjoin = "Message.receiver_id == User.id",
                              backref=db.backref("message_received", lazy='dynamic')
                              )
    #root_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    #root = db.relationship('Message',
    #                        remote_side=[id],
    #                        backref=db.backref('leafs', remote_side=[root_id], lazy='dynamic')
    #                        )
    parent_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    children = db.relationship('Message',
                                backref=db.backref('parent', remote_side=[id]),
                                lazy='dynamic'
                              )
   
    def __repr__(self):
        return '<Message sender:{} receiver:{} subject:{}>'\
                    .format(self.sender_id, self.receiver_id, self.subject)

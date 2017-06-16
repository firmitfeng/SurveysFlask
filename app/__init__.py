# -*- coding: utf-8 -*-

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
from flask_login import LoginManager
from flask import Blueprint

from config import config


bootstrap = Bootstrap()
db = SQLAlchemy()
csrf = CsrfProtect()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.login'
login_manager.login_message = u'请先登录'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)


    from .main import main
    app.register_blueprint(main)

    from .manage import manage
    app.register_blueprint(manage, url_prefix='/manage')

    #from .api import api
    #app.register_blueprint(api, url_prefix='/api')

    return app


# -*- coding: utf-8 -*- 
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class config:
    SECRET_KEY = '79fd52ff278537daba0678417fe31a486f9847ea'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    ENTRIES_PER_PAGE = 20

    THREADED = True

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(config):
    DEBUG = True
    BOOTSTRAP_SERVE_LOCAL = True
    #这个是跟踪模版加载、解析的选项
    #EXPLAIN_TEMPLATE_LOADING = True
    #这个是显示sql引擎工作过程的参数
    #SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://clinical:12345678@localhost/clinical'

class TestingConfig(config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class ProductionConfig(config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://clinical:12345678@localhost/clinical'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}

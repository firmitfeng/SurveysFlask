# -*- coding: utf-8 -*-

from flask import Blueprint

main = Blueprint(
        'main',
        __name__,
        template_folder = 'templates',
        static_folder='static',
        static_url_path='/static/main'
    )


#import views
from . import views, survey, errors


# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

#import os
#import random
#from datetime import datetime

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
#from flask import Flask, render_template, url_for, session, redirect, flash, make_response

from app import create_app, db


app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


if __name__ == "__main__":
    manager.run()


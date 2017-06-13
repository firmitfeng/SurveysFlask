# -*- coding: utf-8 -*- 

import sys
sys.path.append('..')

import pymysql

from datetime import datetime

from app import db
from app.models import Permission, PostStatus, PostType
from app.models import SiteMeta, Role, User, UserMeta, Post, PostMeta, Tag, \
        ActLog, Privacy, Attachment

def getRecords(cursor, tag):
    sql = 'SELECT * from news where cate="%s"' % tag
    try:
        cursor.execute("SET NAMES 'utf8'")
        cursor.execute(sql)
        result = cursor.fetchall()
    except:
        print sql
        print "DB Error"

    return result

def RecordToPost(records, tag):
    if tag == 0:
        tag = Tag.query.filter_by(abbr='news').first()
    elif tag == 1:
        tag = Tag.query.filter_by(abbr='notice').first()
    elif tag == 2:
        tag = Tag.query.filter_by(abbr='xshd').first()
    elif tag == 3:
        tag = Tag.query.filter_by(abbr='xgtz').first()
    
    posts = [Post(title=r[1].decode('utf-8'), content=r[2].decode('utf-8'), \
            ctime=r[3], uptime=r[3], is_top=r[5], tags=[tag], author_id=1, \
            status=PostStatus.PUB, types=PostType.POST) \
            for r in records]

#    posts = [{'title':r[1].decode('utf-8'), 'content':r[2].decode('utf-8'), \
#            'ctime':r[3], 'uptime':r[3], 'is_top':r[5], 'tag':tag, \
#            'author_id':1, 'status':PostStatus.PUB, 'types':PostType.POST}\
#            for r in records]

    return posts

def DBTrans():
    psyweb= pymysql.connect("localhost","psyweb", '12345678', 'psyweb')
    cursor = psyweb.cursor()

    for t in range(0,4):
        results = getRecords(cursor, t)
        posts = RecordToPost(results, t)
        #print posts[0]
        db.session.add_all(posts)
        db.session.commit()

    psyweb.close()

if __name__ == '__main__':
    DBTrans()

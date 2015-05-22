# -*- coding: utf-8 -*-

from sqlalchemy import Column, Table, ForeignKey, types
from sqlalchemy.ext.mutable import Mutable
#from werkzeug import generate_password_hash, check_password_hash
from geoalchemy2 import Geometry
from flask.ext.login import UserMixin

from .constants import OPEN, TOKEN, DONE, MAX_POST_LENGTH, MAX_FILENAME_LENGTH
from ..extensions import db
from ..utils import get_current_time, SEX_TYPE, STRING_LEN

'''
Author, location, datetime, status, expiration date,
	 keywords(classification, food, labor, commute), short text, 
	 long html allow picture(how bbs post is stored) and so on.
	—>biders many-many
	—>conversation 1-many
	—>deal 1-1
	message all other
	'''
usertakepost = db.Table('postreply', 
    db.Column('post_id', db.Integer, ForeignKey('posts.id')),
    db.Column('user_id', db.Integer, ForeignKey('users.id'))
)
#Post-keyword relation, many-many
posttags = db.Table('posttags',
    db.Column('tag', db.String, db.ForeignKey('tags.tag')),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
)

class Post(db.Model):
    __tablename__ = 'posts'
    __searchable__ = ['text']
    id = Column(db.Integer, primary_key=True)
    text = Column(db.String(MAX_POST_LENGTH))
    user_id = Column(db.Integer, ForeignKey('users.id'))
    timestamp = Column(db.DateTime)
    effective_on = Column(db.DateTime)
    expire_on = Column(db.DateTime, default=None)
    tags = db.relationship('Tag', secondary=posttags,
                        backref=db.backref('posts', lazy='dynamic'))
    
#    location = Column(Geometry('POINT'))
#    replied = db.relationship('User', secondary=postreply, 
#                               backref=db.backref('replies', lazy='dynamic'), 
#                               lazy='dynamic')
    status = Column(db.Integer, default=OPEN) 
    has_photo = Column(db.Boolean(), default=False)

    def __repr__(self):
        return '<Post %r>' % (self.body)

    def token_by(self, user):
        #token by user
        self.status = TOKEN
        return self

#Tags
class Tag(db.Model):
    __tablename__ = 'tags'
    tag = Column(db.String(50), primary_key=True, unique=True)

#Post-photo relation, 1-many
class Photo(db.Model):
    __tablename__ = 'photos'
    id = Column(db.Integer(), primary_key=True)
    photo = Column(db.String(MAX_FILENAME_LENGTH), unique=True)
    post_id = Column(db.Integer, db.ForeignKey('posts.id'))
    post = db.relationship("Post", uselist=False, backref="photo")

class Chat(db.Model):
    """docstring for Conversation"""
    id = Column(db.Integer, primary_key=True)
    post = Column(db.Integer, db.ForeignKey('posts.id'))
    poster = Column(db.Integer, db.ForeignKey('users.id'))
    replier = Column(db.Integer, db.ForeignKey('users.id'))

class Message(db.Model):
    """docstring for Conversation"""
    id = Column(db.Integer, primary_key=True)
    in_chat = Column(db.Integer, db.ForeignKey('chat.id'))
    content = Column(db.Integer, db.ForeignKey('users.id'))

		
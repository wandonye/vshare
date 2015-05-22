# -*- coding: utf-8 -*-

from sqlalchemy import Column, Table, ForeignKey, types
from sqlalchemy.ext.mutable import Mutable
#from werkzeug import generate_password_hash, check_password_hash
from geoalchemy2 import Geometry
from flask.ext.login import UserMixin

from .constants import *
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

		
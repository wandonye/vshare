# -*- coding: utf-8 -*-

from sqlalchemy import Column, types
from sqlalchemy.ext.mutable import Mutable
from werkzeug import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

from ..extensions import db
from ..utils import get_current_time, SEX_TYPE, STRING_LEN
from .constants import USER, USER_ROLE, ADMIN, INACTIVE, USER_STATUS
from ..post.models import Post

#following relation, many-many
followrel = db.Table('followrel',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)

class UserDetail(db.Model):

    __tablename__ = 'user_details'

    id = Column(db.Integer, primary_key=True)

    birth_day = Column(db.DateTime, nullable=True)
    phone = Column(db.String(STRING_LEN))
    url = Column(db.String(STRING_LEN))
    deposit = Column(db.Numeric)
    location = Column(db.String(STRING_LEN))
    bio = Column(db.String(STRING_LEN))

    language = Column(db.String(5)) #'en','zh', etc
    sex_code = Column(db.Integer) #0 female, 1 male, 2 other
    avatar = Column(db.String(STRING_LEN))

    @property
    def sex(self):
        return SEX_TYPE.get(self.sex_code)

    created_time = Column(db.DateTime, default=get_current_time)


class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(STRING_LEN), nullable=False, unique=True)
    openid = Column(db.String(STRING_LEN), unique=True)
    activation_key = Column(db.String(STRING_LEN))
    created_time = Column(db.DateTime, default=get_current_time)

    email = Column(db.String(STRING_LEN), nullable=False, unique=True)
    confirmed_at = Column(db.DateTime)

    first_name = Column(db.String(STRING_LEN), nullable=False, default='')
    last_name = Column(db.String(STRING_LEN), nullable=False, default='')

    avatar = Column(db.String(STRING_LEN))

    _password = Column('password', db.String(STRING_LEN), nullable=False)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = generate_password_hash(password)
    # Hide password encryption by exposing password field only.
    password = db.synonym('_password',
                          descriptor=property(_get_password,
                                              _set_password))

    def check_password(self, password):
        if self.password is None:
            return False
        return check_password_hash(self.password, password)

    # ================================================================
    role_code = Column(db.SmallInteger, default=USER, nullable=False)

    @property
    def role(self):
        return USER_ROLE[self.role_code]

    def is_admin(self):
        return self.role_code == ADMIN

    # ================================================================
    # One-to-many relationship between users and user_statuses.
    status_code = Column(db.SmallInteger, default=INACTIVE)

    @property
    def status(self):
        return USER_STATUS[self.status_code]

    # ================================================================
    # One-to-one (uselist=False) relationship between users and user_details.
    user_detail_id = Column(db.Integer, db.ForeignKey("user_details.id"))
    user_detail = db.relationship("UserDetail", uselist=False, backref="user")

    # ================================================================
    # One-to-many relationship between users and posts.
    posts = db.relationship("Post", backref='author', lazy='dynamic')

    # ================================================================
    # Follow / Following
    following = db.relationship('User',
                               secondary=followrel,
                               primaryjoin=(followrel.c.follower_id == id),
                               secondaryjoin=(followrel.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    @property
    def num_followers(self):
        if self.followers:
            return self.followers.count()
        return 0

    @property
    def num_following(self):
        return self.following.count()

    def is_following(self, user):
        return self.following.filter(
            followrel.c.followed_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.following.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)
            return self

    def get_following_query(self):
        return User.query.filter(User.id.in_(self.following or set()))

    def get_followers_query(self):
        return User.query.filter(User.id.in_(self.followers or set()))

    def followed_posts(self):
        return Post.query.join(
            followrel, (followrel.c.followed_id == Post.user_id)).filter(
                followrel.c.follower_id == self.id).order_by(
                    Post.timestamp.desc())

#        return Post.query.filter(Post.author in self.get_following_query()).order_by(
#                    Post.effective_on.desc())

    # ================================================================
    # Class methods

    @classmethod
    def authenticate(cls, login, password):
        user = cls.query.filter(db.or_(User.name == login, User.email == login)).first()

        if user:
            authenticated = user.check_password(password)
        else:
            authenticated = False

        return user, authenticated

    @classmethod
    def search(cls, keywords):
        criteria = []
        for keyword in keywords.split():
            keyword = '%' + keyword + '%'
            criteria.append(db.or_(
                User.name.ilike(keyword),
                User.email.ilike(keyword),
            ))
        q = reduce(db.and_, criteria)
        return cls.query.filter(q)

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first_or_404()

    def check_name(self, name):
        return User.query.filter(db.and_(User.name == name, User.email != self.id)).count() == 0

# -*- coding: utf-8 -*-

import os

from vshare.utils import make_dir, INSTANCE_FOLDER_PATH


class BaseConfig(object):

    PROJECT = "vshare"

    # Get app root path, also can use flask.root_path.
    # ../../config.py
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    DEBUG = False
    TESTING = False

    ADMINS = ['dongning.wang@gmail.com']

    # http://flask.pocoo.org/docs/quickstart/#sessions
    SECRET_KEY = 'secret key'

    LOG_FOLDER = os.path.join(INSTANCE_FOLDER_PATH, 'logs')
    make_dir(LOG_FOLDER)

    # File upload, should override in production.
    # Limited the maximum allowed payload to 16 megabytes.
    # http://flask.pocoo.org/docs/patterns/fileuploads/#improving-uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(INSTANCE_FOLDER_PATH, 'uploads')
    make_dir(UPLOAD_FOLDER)


class DefaultConfig(BaseConfig):

    DEBUG = True

    # Flask-Sqlalchemy: http://packages.python.org/Flask-SQLAlchemy/config.html
    SQLALCHEMY_ECHO = True
    # SQLITE for prototyping.
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + INSTANCE_FOLDER_PATH + '/db.sqlite'
    # MYSQL for production.
    #SQLALCHEMY_DATABASE_URI = 'mysql://username:password@server/db?charset=utf8'
    #pgsql
    SQLALCHEMY_DATABASE_URI = 'postgresql://pgsql:pgsql@localhost/vshare'

    # Flask-babel: http://pythonhosted.org/Flask-Babel/
    ACCEPT_LANGUAGES = ['zh']
    BABEL_DEFAULT_LOCALE = 'en'

    # Flask-cache: http://pythonhosted.org/Flask-Cache/
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 60

    # Flask-mail: http://pythonhosted.org/flask-mail/
    # https://bitbucket.org/danjac/flask-mail/issue/3/problem-with-gmails-smtp-server
    MAIL_DEBUG = DEBUG
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    # Should put MAIL_USERNAME and MAIL_PASSWORD in production under instance folder.
    MAIL_USERNAME = 'dongning.wang@gmail.com'
    MAIL_PASSWORD = 'Ljgoogle2254'
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    # Flask-openid: http://pythonhosted.org/Flask-OpenID/
    OPENID_FS_STORE_PATH = os.path.join(INSTANCE_FOLDER_PATH, 'openid')
    make_dir(OPENID_FS_STORE_PATH)

    # User:
    USER_CONFIRM_EMAIL_EXPIRATION = 2*24*3600   # 2 days

# Set default template files
#    USER_CHANGE_PASSWORD_TEMPLATE = 'flask_user/change_password.html'
#    USER_CHANGE_USERNAME_TEMPLATE = 'flask_user/change_username.html'
#    USER_FORGOT_PASSWORD_TEMPLATE = 'flask_user/forgot_password.html'
#login_template                = sd('USER_LOGIN_TEMPLATE',            'flask_user/login.html')
#manage_emails_template        = sd('USER_MANAGE_EMAILS_TEMPLATE',    'flask_user/manage_emails.html')
#register_template             = sd('USER_REGISTER_TEMPLATE',         'flask_user/register.html')
#resend_confirm_email_template = sd('USER_RESEND_CONFIRM_EMAIL_TEMPLATE', 'flask_user/resend_confirm_email.html')
#reset_password_template       = sd('USER_RESET_PASSWORD_TEMPLATE',   'flask_user/reset_password.html')
#user_profile_template         = sd('USER_PROFILE_TEMPLATE',          'flask_user/user_profile.html')

# Set default email template files
#confirm_email_email_template    = sd('USER_CONFIRM_EMAIL_EMAIL_TEMPLATE',    'flask_user/emails/confirm_email')
#forgot_password_email_template  = sd('USER_FORGOT_PASSWORD_EMAIL_TEMPLATE',  'flask_user/emails/forgot_password')
#password_changed_email_template = sd('USER_PASSWORD_CHANGED_EMAIL_TEMPLATE', 'flask_user/emails/password_changed')
#registered_email_template       = sd('USER_REGISTERED_EMAIL_TEMPLATE',       'flask_user/emails/registered')
#username_changed_email_template = sd('USER_USERNAME_CHANGED_EMAIL_TEMPLATE', 'flask_user/emails/username_changed')


class TestConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://pgsql:pgsql@localhost/vshare'

# -*- coding: utf-8 -*-

from flask import Markup

from flask.ext.wtf import Form
from wtforms import (ValidationError, HiddenField, BooleanField, TextField,
        PasswordField, SubmitField)
from wtforms.validators import Required, Length, EqualTo, Email, DataRequired
from flask.ext.wtf.html5 import EmailField
from vshare.translations import lazy_gettext as _

from ..user import User
from ..utils import (PASSWORD_LEN_MIN, PASSWORD_LEN_MAX,
        USERNAME_LEN_MIN, USERNAME_LEN_MAX)

# **************************
# ** Validation Functions **
# **************************

def password_validator(form, field):
    """ Password must have one lowercase letter, one uppercase letter and one digit."""
    # Convert string to list of characters
    password = list(field.data)
    password_length = len(password)

    # Count lowercase, uppercase and numbers
    lowers = uppers = digits = 0
    for ch in password:
        if ch.islower(): lowers+=1
        if ch.isupper(): uppers+=1
        if ch.isdigit(): digits+=1

    # Password must have one lowercase letter, one uppercase letter and one digit
    is_valid = password_length>=6 and lowers and uppers and digits
    if not is_valid:
        raise ValidationError(_('Password must have at least 6 characters with one lowercase letter, one uppercase letter and one number'))

def username_validator(form, field):
    """ Username must cont at least 3 alphanumeric characters long"""
    username = field.data
    if len(username) < 3:
        raise ValidationError(_('Username must be at least 3 characters long'))
    valid_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._'
    chars = list(username)
    for char in chars:
        if char not in valid_chars:
            raise ValidationError(_("Username may only contain letters, numbers, '-', '.' and '_'."))

def unique_username_validator(form, field):
    """ Username must be unique"""
    if User.query.filter_by(name=field.data).first() is not None:
        raise ValidationError(u'This username is taken')


def unique_email_validator(form, field):
    """ Username must be unique"""
    if User.query.filter_by(email=field.data).first() is not None:
        raise ValidationError(u'This email is taken')

class LoginForm(Form):
    next = HiddenField()
    login = TextField(_('Username or Email'), [Required()])
    password = PasswordField(_('Password'), [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    remember = BooleanField(_('Remember me'))
    submit = SubmitField(_('Sign in'))


class SignupForm(Form):
    next = HiddenField()

    name = TextField(_('Username'), validators=[
            DataRequired(_('Username is required')),
            unique_username_validator])
    email = EmailField(_('Email'), validators=[
            DataRequired(_('Email is required')),
            Email(_('Invalid Email')),
            unique_email_validator])
    password = PasswordField(_('Password'), validators=[
            DataRequired(_('Password is required'))],
            #description=_('Password must have one lowercase letter, one uppercase letter and one digit.')
            )
    retype_password = PasswordField(_('Retype Password'), validators=[
            EqualTo('password', message=_('Password and Retype Password did not match'))])

    agree = BooleanField(u'Agree to the ' +
        Markup('<a target="blank" href="/terms">Terms of Service</a>'), [Required()])
    submit = SubmitField('Sign up')

    def validate(self):
        # remove certain form fields depending on user manager config
        #    delattr(self, 'retype_password')
        # Add custom username validator if needed
        #
        # Add custom password validator if needed
        has_been_added = False
        for v in self.password.validators:
            if v==password_validator:
                has_been_added = True
        if not has_been_added:
            self.password.validators.append(password_validator)
        # Validate field-validators
        if not super(SignupForm, self).validate():
            return False
        # All is well
        return True

class RecoverPasswordForm(Form):
    email = EmailField(_('Your Email'), [Email()])
    submit = SubmitField(_('Send instructions'))


class ChangePasswordForm(Form):
    activation_key = HiddenField()
    password = PasswordField(_('Password'), [Required()])
    password_again = PasswordField(_('Password again'), [EqualTo('password', message="Passwords don't match")])
    submit = SubmitField('Save')


class ReauthForm(Form):
    next = HiddenField()
    password = PasswordField(_('Password'), [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    submit = SubmitField('Reauthenticate')


class OpenIDForm(Form):
    openid = TextField(_('Your OpenID'), [Required()])
    submit = SubmitField(_('Log in with OpenID'))


class CreateProfileForm(Form):
    openid = HiddenField()
    name = TextField(_('Username'), validators=[
            DataRequired(_('Username is required')),
            unique_username_validator])
    email = EmailField(_('Email'), validators=[
            DataRequired(_('Email is required')),
            Email(_('Invalid Email')),
            unique_email_validator])
    password = PasswordField(_('Password'), validators=[
            DataRequired(_('Password is required'))],
            description=u'Password must have one lowercase letter, one uppercase letter and one digit.')
    retype_password = PasswordField(_('Retype Password'), validators=[
            EqualTo('password', message=_('Password and Retype Password did not match'))])
    submit = SubmitField(u'Create Profile')

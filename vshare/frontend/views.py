# -*- coding: utf-8 -*-

from uuid import uuid4
from datetime import datetime
from flask import (Blueprint, render_template, current_app, request,
                   flash, url_for, redirect, session, abort)
from flask.ext.mail import Message
from flask.ext.babel import gettext as _
from flask.ext.login import login_required, login_user, current_user, logout_user, confirm_login, login_fresh

from ..user import User, UserDetail, emails, signals
from ..extensions import db, mail, login_manager, oid, token_manager
from .forms import SignupForm, LoginForm, RecoverPasswordForm, ReauthForm, ChangePasswordForm, OpenIDForm, CreateProfileForm
from ..post.constants import POSTS_PER_PAGE
from ..post import Post

frontend = Blueprint('frontend', __name__)


@frontend.route('/login/openid', methods=['GET', 'POST'])
@oid.loginhandler
def login_openid():
    if current_user.is_authenticated():
        return redirect(url_for('user.index'))

    form = OpenIDForm()
    if form.validate_on_submit():
        openid = form.openid.data
        current_app.logger.debug('login with openid(%s)...' % openid)
        return oid.try_login(openid, ask_for=['email', 'fullname', 'nickname'])
    return render_template('frontend/login_openid.html', form=form, error=oid.fetch_error())


@oid.after_login
def create_or_login(resp):
    user = User.query.filter_by(openid=resp.identity_url).first()
    if user and login_user(user):
        flash('Logged in', 'success')
        return redirect(oid.get_next_url() or url_for('user.index'))
    return redirect(url_for('frontend.create_profile', next=oid.get_next_url(),
            name=resp.fullname or resp.nickname, email=resp.email,
            openid=resp.identity_url))


@frontend.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    if current_user.is_authenticated():
        return redirect(url_for('user.index'))

    form = CreateProfileForm(name=request.args.get('name'),
            email=request.args.get('email'),
            openid=request.args.get('openid'))

    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()

        if login_user(user):
            return redirect(url_for('user.index'))

    return render_template('frontend/create_profile.html', form=form)


@frontend.route('/')
def index():
    current_app.logger.debug('debug')

    page = int(request.args.get('page', 1))
    if current_user.is_authenticated():
        return redirect(url_for('user.index'))

    pagination = User.query.paginate(page=page, per_page=10)
    return render_template('index.html', pagination=pagination)


@frontend.route('/search')
def search():
    keywords = request.args.get('keywords', '').strip()
    pagination = None
    if keywords:
        page = int(request.args.get('page', 1))
        pagination = User.search(keywords).paginate(page, 1)
    else:
        flash(_('Please input keyword(s)'), 'error')
    return render_template('frontend/search.html', pagination=pagination, keywords=keywords)


@frontend.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect(url_for('user.index'))

    form = LoginForm(login=request.args.get('login', None),
                     next=request.args.get('next', None))

    if form.validate_on_submit():
        user, authenticated = User.authenticate(form.login.data,
                                    form.password.data)

        if user and authenticated:
            remember = request.form.get('remember') == 'y'
            if login_user(user, remember=remember):
                flash(_("Logged in"), 'success')
            return redirect(form.next.data or url_for('user.index'))
        else:
            flash(_('Sorry, invalid login'), 'error')

    return render_template('frontend/login.html', form=form)


@frontend.route('/reauth', methods=['GET', 'POST'])
@login_required
def reauth():
    form = ReauthForm(next=request.args.get('next'))

    if request.method == 'POST':
        user, authenticated = User.authenticate(current_user.name,
                                    form.password.data)
        if user and authenticated:
            confirm_login()
            current_app.logger.debug('reauth: %s' % session['_fresh'])
            flash(_('Reauthenticated.'), 'success')
            return redirect('/change_password')

        flash(_('Password is wrong.'), 'error')
    return render_template('frontend/reauth.html', form=form)


@frontend.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('Logged out'), 'success')
    return redirect(url_for('frontend.index'))


@frontend.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated():
        return redirect(url_for('user.index'))

    form = SignupForm(next=request.args.get('next'))

    if form.validate_on_submit():
        user = User()
        user.user_detail = UserDetail()
        form.populate_obj(user)

        db.session.add(user)
        db.session.commit()

        try:
            # Send 'registered' email
            _send_registered_email(user)
        except Exception as e:
            # delete new User object if send  fails
            db.session.delete(user)
            db.session.commit()
            raise e

        if login_user(user):
            return redirect(form.next.data or url_for('user.index'))


    return render_template('frontend/signup.html', form=form)


@frontend.route('/change_password', methods=['GET', 'POST'])
def change_password():
    user = None
    if current_user.is_authenticated():
        if not login_fresh():
            return login_manager.needs_refresh()
        user = current_user
    elif 'activation_key' in request.values and 'email' in request.values:
        activation_key = request.values['activation_key']
        email = request.values['email']
        user = User.query.filter_by(activation_key=activation_key) \
                         .filter_by(email=email).first()

    if user is None:
        abort(403)

    form = ChangePasswordForm(activation_key=user.activation_key)

    if form.validate_on_submit():
        user.password = form.password.data
        user.activation_key = None
        db.session.add(user)
        db.session.commit()

        flash(_("Your password has been changed, please log in again"),
              "success")
        return redirect(url_for("frontend.login"))

    return render_template("frontend/change_password.html", form=form)


@frontend.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = RecoverPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            flash('Please see your email for instructions on '
                  'how to access your account', 'success')

            user.activation_key = str(uuid4())
            db.session.add(user)
            db.session.commit()

            url = url_for('frontend.change_password', email=user.email, activation_key=user.activation_key, _external=True)
            html = render_template('macros/_reset_password.html', project=current_app.config['PROJECT'], username=user.name, url=url)
            message = Message(subject='Reset your password in ' + current_app.config['PROJECT'], html=html, recipients=[user.email])
            mail.send(message)

            return render_template('frontend/reset_password.html', form=form)
        else:
            flash(_('Sorry, no user found for that email address'), 'error')

    return render_template('frontend/reset_password.html', form=form)

@frontend.route('/confirm_email',methods=['GET'])
def confirm_email():
    """ Verify email confirmation token and activate the user account."""
    # Verify token
    token = request.args['token']
    is_valid, has_expired, object_id = token_manager.verify_token(token,
                                       current_app.config['USER_CONFIRM_EMAIL_EXPIRATION'])

    if has_expired:
        flash(_('Your confirmation token has expired.'), 'error')
        return redirect(url_for('user.login'))

    if not is_valid:
        flash(_('Invalid confirmation token.'), 'error')
        return redirect(url_for('user.login'))

    # Confirm email by setting User.active=True and User.confirmed_at=utcnow()
    user = User.query.get(object_id)

    if user:
        user.confirmed_at = datetime.utcnow()
        #user.set_active(True)
        db.session.commit()
    else:                                               # pragma: no cover
        flash(_('Invalid confirmation token.'), 'error')
        return redirect(url_for('frontend.login'))

    # Send email_confirmed signal
    signals.user_confirmed_email.send(current_app._get_current_object(), user=user)

    # Prepare one-time system message
    flash(_('Your email has been confirmed.'), 'success')

    # Auto-login after confirm or redirect to login page
    next = request.args.get('next', _endpoint_url('frontend.login'))
    return _do_login_user(user, next)                       # auto-login
    #return redirect(url_for('frontend.login')+'?next='+next)    # redirect to login page

@frontend.route('/help')
def help():
    return render_template('frontend/footers/help.html', active="help")

def _send_registered_email(user):
    # Send 'confirm_email' or 'registered' email
    # Generate confirm email link
    object_id = int(user.get_id())
    token = token_manager.generate_token(object_id)
    confirm_email_link = url_for('frontend.confirm_email', token=token, _external=True)

    # Send email
    emails.send_registered_email(user, user.email, confirm_email_link)

    # Prepare one-time system message
    email = user.email
    flash(_('A confirmation email has been sent to %(email)s with instructions to complete your registration.', email=email), 'success')

def _send_confirm_email(user):

    # Send 'confirm_email' or 'registered' email
    # Generate confirm email link
    object_id = int(user.get_id())
    token = token_manager.generate_token(object_id)
    confirm_email_link = url_for('frontend.confirm_email', token=token, _external=True)

    # Send email
    emails.send_confirm_email_email(user, user.email, confirm_email_link)

    # Prepare one-time system message
    email = user.email
    flash(_('A confirmation email has been sent to %(email)s with instructions to complete your registration.', email=email), 'success')

def _do_login_user(user, next, remember_me=False):
    # User must have been authenticated
    if not user: return unauthenticated()

    # Check if user account has been disabled
#    if not user.is_active():
#        flash(_('Your account has not been enabled.'), 'error')
#        return redirect(url_for('user.home'))

    # Check if user has a confirmed email address
#    if user.has_confirmed_email():
#        url = url_for('user.resend_confirm_email')
#        flash(_('Your email address has not yet been confirmed. Check your email Inbox and Spam folders for the confirmation email or <a href="%(url)s">Re-send confirmation email</a>.', url=url), 'error')
#        return redirect(url_for('user.home'))

    # Use Flask-Login to sign in user
    #print('login_user: remember_me=', remember_me)
    login_user(user, remember=remember_me)

    # Send user_logged_in signal
    signals.user_logged_in.send(current_app._get_current_object(), user=user)

    # Prepare one-time system message
    flash(_('You have signed in successfully.'), 'success')

    # Redirect to 'next' URL
    return redirect(next)

def _endpoint_url(endpoint):
    url = '/'
    if endpoint:
        url = url_for(endpoint)
    return url
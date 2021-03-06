""" This file contains email sending functions for Flask-User.
    It uses Jinja2 to render email subject and email message. It uses Flask-Mail to send email.

    :copyright: (c) 2013 by Ling Thio
    :author: Ling Thio (ling.thio@gmail.com)
    :license: Simplified BSD License, see LICENSE.txt for more details."""

import smtplib
import socket
from flask import current_app, render_template

def _render_email(filename, **kwargs):
    # Render subject
    subject = render_template(filename+'_subject.txt', **kwargs)
    # Make sure that subject lines do not contain newlines
    subject = subject.replace('\n', ' ')
    subject = subject.replace('\r', ' ')
    # Render HTML message
    html_message = render_template(filename+'_message.html', **kwargs)
    # Render text message
    text_message = render_template(filename+'_message.txt', **kwargs)

    return (subject, html_message, text_message)

def send_email(recipient, subject, html_message, text_message):
    """ Send email from default sender to 'recipient' """

    class SendEmailError(Exception):
        pass

    # Make sure that Flask-Mail has been installed
    try:
        from flask_mail import Message
    except:
        raise SendEmailError("Flask-Mail has not been installed. Use 'pip install Flask-Mail' to install Flask-Mail.")

    # Make sure that Flask-Mail has been initialized
    mail_engine = current_app.extensions.get('mail', None)
    if not mail_engine:
        raise SendEmailError('Flask-Mail has not been initialized. Initialize Flask-Mail or disable USER_SEND_PASSWORD_CHANGED_EMAIL, USER_SEND_REGISTERED_EMAIL and USER_SEND_USERNAME_CHANGED_EMAIL')

    try:

        # Construct Flash-Mail message
        message = Message(subject,
                recipients=[recipient],
                html = html_message,
                body = text_message)
        mail_engine.send(message)

    # Print helpful error messages on exceptions
    except (socket.gaierror, socket.error) as e:
        raise SendEmailError('SMTP Connection error: Check your MAIL_HOSTNAME or MAIL_PORT settings.')
    except smtplib.SMTPAuthenticationError:
        raise SendEmailError('SMTP Authentication error: Check your MAIL_USERNAME and MAIL_PASSWORD settings.')

def _get_primary_email(user):
    db_adapter = user_manager.db_adapter
    if db_adapter.UserEmailClass:
        user_email = db_adapter.find_first_object(db_adapter.UserEmailClass,
                user_id=int(user.get_id()),
                is_primary=True)
        return user_email.email if user_email else None
    else:
        return user.email


def send_confirm_email_email(user, user_email, confirm_email_link):
    # Verify certain conditions

    # Retrieve email address from User or UserEmail object
    email = user_email.email if user_email else user.email
    assert(email)

    # Render subject, html message and text message
    subject, html_message, text_message = _render_email(
            confirm_email_email_template,
            user=user,
            app_name=user_manager.app_name,
            confirm_email_link=confirm_email_link)

    # Send email message using Flask-Mail
    send_email(email, subject, html_message, text_message)

def send_forgot_password_email(user, user_email, reset_password_link):
    # Verify certain conditions

    # Retrieve email address from User or UserEmail object
    email = user_email.email if user_email else user.email
    assert(email)

    # Render subject, html message and text message
    subject, html_message, text_message = _render_email(
            forgot_password_email_template,
            user=user,
            app_name=user_manager.app_name,
            reset_password_link=reset_password_link)

    # Send email message using Flask-Mail
    send_email(email, subject, html_message, text_message)

def send_password_changed_email(user):
    # Verify certain conditions

    # Retrieve email address from User or UserEmail object
    email = _get_primary_email(user)
    assert(email)

    # Render subject, html message and text message
    subject, html_message, text_message = _render_email(
            password_changed_email_template,
            user=user,
            app_name=app_name)

    # Send email message using Flask-Mail
    send_email(email, subject, html_message, text_message)

def send_registered_email(user, email, confirm_email_link):    # pragma: no cover
    # Verify certain conditions

    # Render subject, html message and text message
    subject, html_message, text_message = _render_email(
            "emails/registered",
            user=user,
            app_name=current_app.config['PROJECT'],
            confirm_email_link=confirm_email_link)

    # Send email message using Flask-Mail
    send_email(email, subject, html_message, text_message)

def send_username_changed_email(user):  # pragma: no cover
    # Verify certain conditions

    # Retrieve email address from User or UserEmail object
    email = _get_primary_email(user)
    assert(email)

    # Render subject, html message and text message
    subject, html_message, text_message = _render_email(
            username_changed_email_template,
            user=user,
            app_name=user_manager.app_name)

    # Send email message using Flask-Mail
    send_email(email, subject, html_message, text_message)


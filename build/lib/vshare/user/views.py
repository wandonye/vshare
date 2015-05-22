# -*- coding: utf-8 -*-

import os

from flask import Blueprint, render_template, send_from_directory, abort, request
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from .models import User
from ..post.constants import POSTS_PER_PAGE

user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/')
@login_required
def index():
    if not current_user.is_authenticated():
        abort(403)

    page = int(request.args.get('page', 1))
    posts = current_user.followed_posts().paginate(page, POSTS_PER_PAGE, False)

#    page = int(request.args.get('page', 1))
#    pagination = User.query.paginate(page=page, per_page=10)
#    return render_template('index.html', pagination=pagination)

    return render_template('user/index.html', user=current_user, posts=posts)


@user.route('/<int:user_id>/profile')
def profile(user_id):
    user = User.get_by_id(user_id)
    return render_template('user/profile.html', user=user)


@user.route('/<int:user_id>/avatar/<path:filename>')
@login_required
def avatar(user_id, filename):
    dir_path = os.path.join(APP.config['UPLOAD_FOLDER'], 'user_%s' % user_id)
    return send_from_directory(dir_path, filename, as_attachment=True)

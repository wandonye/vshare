
from flask.ext.wtf import Form
from wtforms import (ValidationError, HiddenField, BooleanField, TextField,
        PasswordField, SubmitField, TextAreaField, FileField)
from wtforms.validators import Required, Length, DataRequired, Optional
from wtforms.fields.html5 import DateField
from vshare.translations import lazy_gettext as _
from ..utils import get_current_time

class PostForm(Form):
    text = TextAreaField(_('Post'), validators=[DataRequired()])
    photo = FileField(_("Upload Photo"), [Optional()])
    effective_on = DateField(_('Effective On'), format='%Y-%m-%d', default=get_current_time())
    expire_on = DateField(_('Expire On'), [Optional()], format='%Y-%m-%d')
    submit = SubmitField(_('Post'))
    tags = TextField(_('Tags'), [Optional()])
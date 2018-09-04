# -*- coding: utf-8 -*-
import tg
from tg.i18n import lazy_ugettext as l_

from tw2.forms import TableForm, TextField, PasswordField, HiddenField
from tw2.core import Required
from .validators import UniqueEmailValidator, UniqueUserValidator
from formencode import validators

class RegistrationForm(TableForm):
    # set additional extra info here to bring them across the registration process
    # you might want to serialize the extra info in json or something similar
    extra = HiddenField()

    user_name = TextField(label=l_('User Name'), validator=UniqueUserValidator(not_empty=True))
    email_address = TextField(label=l_('Email'), validator=UniqueEmailValidator(not_empty=True))
    password = PasswordField(label=l_('Password'), validator=Required)
    password_confirm = PasswordField(label=l_('Confirm Password'), validator=Required)
    validator = validators.FieldsMatch('password', 'password_confirm')

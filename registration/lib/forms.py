# -*- coding: utf-8 -*-

from tw.api import WidgetsList
from tw.forms import TableForm, TextField, PasswordField
from tw.forms import validators
from validators import UniqueEmailValidator, UniqueUserValidator
from tg.i18n import lazy_ugettext as l_

class RegistrationForm(TableForm):
    class fields(WidgetsList):
        user_name = TextField(label_text=l_('User Name'), validator=UniqueUserValidator(not_empty=True))
        email_address = TextField(label_text=l_('Email'), validator=UniqueEmailValidator(not_empty=True))
        password = PasswordField(label_text=l_('Password'), validator=validators.UnicodeString(not_empty=True))
        password_confirm = PasswordField(label_text=l_('Confirm Password'),
                                         validator=validators.UnicodeString(not_empty=True))

    validator = validators.Schema(chained_validators = [validators.FieldsMatch('password', 'password_confirm')])
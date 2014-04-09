import re
import tg
from tg.i18n import ugettext as _
from formencode import Invalid
from formencode import validators
from tgext.pluggable import app_model


class UniqueUserValidator(validators.UnicodeString):
    outputEncoding=None

    def validate_python(self, value, state):
        super(UniqueUserValidator, self).validate_python(value, state)
        if re.match("^[a-zA-Z0-9_-]*[a-zA-Z_-][a-zA-Z0-9_-]*$", value):
            user = tg.config['registration_dal'].get_user_by_user_name(value)
            if user:
                raise Invalid(_('Username already in use.'), value, state)
        else:
            raise Invalid(_('Invalid username'), value, state)


class UniqueEmailValidator(validators.String):
    def validate_python(self, value, state):
        super(UniqueEmailValidator, self).validate_python(value, state)
        if re.match("^(([A-Za-z0-9]+_+)|([A-Za-z0-9]+\-+)|([A-Za-z0-9]+\.+)|([A-Za-z0-9]+\++))*[A-Za-z0-9]+@((\w+\-+)|(\w+\.))*\w{1,63}\.[a-zA-Z]{2,6}$", value):
            user = tg.config['registration_dal'].get_user_by_email(value)
            if user:
                raise Invalid(_('Email address has already been taken'), value, state)
        else:
            raise Invalid(_('Invalid email'), value, state)

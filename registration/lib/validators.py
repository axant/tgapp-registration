import re
from tg import request
from tg.i18n import ugettext as _
from registration.model import DBSession, Registration
from formencode import Invalid
from tw.forms import validators

from tgext.pluggable import app_model

class UniqueUserValidator(validators.UnicodeString):
    def validate_python(self, value, state):
        super(UniqueUserValidator, self).validate_python(value, state)
        if re.match("^[a-zA-Z0-9_-]*[a-zA-Z_-][a-zA-Z0-9_-]*$", value):
            reg = DBSession.query(app_model.User).filter_by(user_name=value).first()
            user = DBSession.query(app_model.User).filter_by(user_name=value).first()
            if reg or user:
                raise Invalid(_('username already in use.'), value, state)
        else:
            raise Invalid(_('Invalid username'), value, state)

class UniqueEmailValidator(validators.String):
    def validate_python(self, value, state):
        super(UniqueEmailValidator, self).validate_python(value, state)
        if re.match("^(([A-Za-z0-9]+_+)|([A-Za-z0-9]+\-+)|([A-Za-z0-9]+\.+)|([A-Za-z0-9]+\++))*[A-Za-z0-9]+@((\w+\-+)|(\w+\.))*\w{1,63}\.[a-zA-Z]{2,6}$", value):
            reg = DBSession.query(app_model.User).filter_by(email_address=value).first()
            user = DBSession.query(app_model.User).filter_by(email_address=value).first()
            if reg or user:
                raise Invalid(_('Email address has already been taken'), value, state)
        else:
            raise Invalid(_('Invalid email'), value, state)
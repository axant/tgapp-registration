# -*- coding: utf-8 -*-
"""Setup the registration application"""

from registration import model
from tgext.pluggable import app_model

def bootstrap(command, conf, vars):
    print 'Bootstrapping registration...'

    p = app_model.Permission(permission_name='registration-admin', description='Permits to manage registrations')
    try:
        model.DBSession.add(p)
    except AttributeError:
        # mute ming complaints
        pass
    model.DBSession.flush()
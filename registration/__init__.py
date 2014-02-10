# -*- coding: utf-8 -*-
"""The tgapp-registration package"""
from tg import hooks, config
from tgext.pluggable import app_model


def plugme(app_config, options):
    app_config['_pluggable_registration_config'] = options
    if app_config.get('use_ming'):
        app_model.configure(app_config['ming_model'])
    hooks.register('after_config', lambda app: register_dal_interface(config, app))
    return dict(appid='registration', global_helpers=False)


def register_dal_interface(app_config, app):
    if app_config.get('use_sqlalchemy'):
        print 'initializing registration with sqla'
        from registration.model.sqla_models import SqlaRegistration
        app_config['registration_dal'] = SqlaRegistration()

    elif app_config.get('use_ming'):
        print 'initializing registration with ming'
        from registration.model.ming_models import MingRegistration
        app_config['registration_dal'] = MingRegistration()

    else:
        raise ValueError('registration should be used with sqlalchemy or ming')

    return app
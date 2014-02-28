# -*- coding: utf-8 -*-
"""The tgapp-registration package"""
from tg import hooks, config
from tg.configuration import milestones
from tgext.pluggable import app_model
from registration.model import patch_global_registration


def plugme(app_config, options):
    app_config['_pluggable_registration_config'] = options
    hooks.register('after_config', register_dal_interface)
    milestones.config_ready.register(patch_global_registration)
    return dict(appid='registration', global_helpers=False)


def register_dal_interface(app):
    if config.get('use_sqlalchemy'):
        print 'initializing registration with sqla'
        from registration.model.sqla_models import SqlaRegistration
        config['registration_dal'] = SqlaRegistration()

    elif config.get('use_ming'):
        print 'initializing registration with ming'
        from registration.model.ming_models import MingRegistration
        config['registration_dal'] = MingRegistration()
    else:
        raise ValueError('registration should be used with sqlalchemy or ming')

    return app

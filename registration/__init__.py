# -*- coding: utf-8 -*-
"""The tgapp-registration package"""
from tg import hooks, config
from tg.configuration import milestones
from tgext.pluggable import app_model
from registration.model import patch_global_registration
import warnings


def plugme(app_config, options):
    if 'mail_subject' in options or 'mail_body' in options or 'mail_rich' in options:
        warnings.warn("mail_* options are now deprecated, use registration.on_complete hook(reg, email_data) "
                      "to customize the outgoing email.", DeprecationWarning, stacklevel=2)

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

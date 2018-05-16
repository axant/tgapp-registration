# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import TGController
from tg import expose, flash, require, url, redirect, validate, config, predicates, hooks
from tg.i18n import ugettext as _

from registration.lib import get_form, send_email
from datetime import datetime
from tgext.pluggable import app_model, instance_primary_key

from formencode.validators import UnicodeString
from registration.model.dal_interface import DalIntegrityError


class RootController(TGController):
    @expose('genshi:registration.templates.register')
    @expose('kajiki:registration.templates.register')
    def index(self, *args, **kw):
        hooks.notify('registration.before_registration_form', args=(kw,))
        config['registration_dal'].clear_expired()
        return dict(form=get_form(), value=kw, action=self.mount_point+'/submit')

    @expose('genshi:registration.templates.admin')
    @expose('kajiki:registration.templates.admin')
    @require(predicates.has_permission('registration-admin'))
    def admin(self, **kw):
        config['registration_dal'].clear_expired()
        pending_activation = config['registration_dal'].pending_activation()
        return dict(registrations=pending_activation)

    @expose()
    @validate(get_form(), error_handler=index)
    def submit(self, *args, **kw):
        hooks.notify('registration.before_registration', args=(kw,))

        new_reg = config['registration_dal'].new(**kw)

        hooks.notify('registration.after_registration', args=(new_reg, kw))
        return redirect(url(self.mount_point + '/complete',
                            params=dict(email=new_reg.email_address)))

    @expose('genshi:registration.templates.complete')
    @expose('kajiki:registration.templates.complete')
    @validate(dict(email=UnicodeString(not_empty=True)), error_handler=index)
    def complete(self, email, **kw):
        reg = config['registration_dal'].by_email(email)
        if not reg:
            # flash(_('Registration not found or already activated'))
            return redirect(self.mount_point)

        # Force resolution of lazy property
        reg.activation_link

        registration_config = config.get('_pluggable_registration_config')
        mail_body = registration_config.get(
            'mail_body',
            _('Please click on this link to confirm your registration')
        )
        if '%(activation_link)s' not in mail_body:
            mail_body += '\n \n %(activation_link)s'

        email_data = {'sender': config['registration.email_sender'],
                      'subject': registration_config.get(
                          'mail_subject', _('Please confirm your registration')
                      ),
                      'body': mail_body,
                      'rich': registration_config.get('mail_rich', '')}

        hooks.notify('registration.on_complete', (reg, email_data))

        email_data['body'] = email_data['body'] % reg.dictified
        email_data['rich'] = email_data['rich'] % reg.dictified

        send_email(reg.email_address, **email_data)
        return dict(email=email, email_data=email_data)

    @expose()
    @validate(dict(code=UnicodeString(not_empty=True)), error_handler=index)
    def activate(self, code, **kw):
        reg = config['registration_dal'].get_inactive(code)
        if not reg:
            flash(_('Registration not found or already activated'), 'error')
            return redirect(self.mount_point)

        u = app_model.User(user_name=reg.user_name,
                           display_name=reg.user_name,
                           email_address=reg.email_address,
                           password=reg.password)

        hooks.notify('registration.before_activation', (reg, u))

        try:
            u = config['registration_dal'].out_of_uow_flush(u)
        except DalIntegrityError:
            flash(_('Username already activated'), 'error')
            return redirect(self.mount_point)

        reg.user_id = instance_primary_key(u)
        reg.password = '******'
        reg.activated = datetime.now()

        hooks.notify('registration.after_activation', (reg, u))

        flash(_('Account succesfully activated'))
        return redirect('/')

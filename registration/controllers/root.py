# -*- coding: utf-8 -*-
"""Main Controller"""
from sqlalchemy.exc import IntegrityError

from tg import TGController
from tg import expose, flash, require, url, lurl, request, redirect, validate, config, predicates
from tg.i18n import ugettext as _, lazy_ugettext as l_

from registration.model import DBSession, Registration
from registration.lib import get_form, send_email
from datetime import datetime
from tgext.pluggable import app_model

from formencode.validators import UnicodeString
import transaction

class RootController(TGController):
    @expose('registration.templates.register')
    def index(self, *args, **kw):
        Registration.clear_expired()
        return dict(form=get_form(), value=kw, action=self.mount_point+'/submit')

    @expose('registration.templates.admin')
    @require(predicates.has_permission('registration-admin'))
    def admin(self, **kw):
        Registration.clear_expired()
        pending_activation = DBSession.query(Registration).filter(Registration.activated==None)
        return dict(registrations=pending_activation)

    @expose()
    @validate(get_form(), error_handler=index)
    def submit(self, *args, **kw):
        hooks = config['hooks'].get('registration.before_registration', [])
        for func in hooks:
            func(kw)

        new_reg = Registration()
        new_reg.email_address = kw['email_address']
        new_reg.user_name = kw['user_name']
        new_reg.password = kw['password']
        new_reg.code = Registration.generate_code(kw['email_address'])
        DBSession.add(new_reg)
        DBSession.flush()

        hooks = config['hooks'].get('registration.after_registration', [])
        for func in hooks:
            func(new_reg, kw)
        return redirect(url(self.mount_point + '/complete',
                            params=dict(email=new_reg.email_address)))

    @expose('registration.templates.complete')
    @validate(dict(email=UnicodeString(not_empty=True)), error_handler=index)
    def complete(self, email, **kw):
        reg = DBSession.query(Registration).filter_by(email_address=email).first()

        if not reg:
            flash(_('Registration not found or already activated'))
            return redirect(self.mount_point)
        registration_config = config.get('_pluggable_registration_config')
        mail_body = registration_config.get('mail_body', _('Please click on this link to confirm your registration')) \
                                       + '\n \n %s'
        email_data = {'sender':config['registration.email_sender'],
                      'subject':registration_config.get('mail_subject', _('Please confirm your registration')),
                      'body':mail_body % reg.activation_link}

        hooks = config['hooks'].get('registration.on_complete', [])
        for func in hooks:
            func(email_data)

        send_email(reg.email_address, email_data['sender'], email_data['subject'], email_data['body'])

        return dict(email = email, email_data=email_data)

    @expose()
    @validate(dict(code=UnicodeString(not_empty=True)), error_handler=index)
    def activate(self, code, **kw):
        reg = Registration.get_inactive(code)
        if not reg:
            flash(_('Registration not found or already activated'))
            return redirect(self.mount_point)

        u = app_model.User(user_name=reg.user_name,
                           display_name=reg.user_name,
                           email_address=reg.email_address,
                           password=reg.password)


        hooks = config['hooks'].get('registration.before_activation', [])
        for func in hooks:
            func(reg, u)

        DBSession.add(u)
        try:
            DBSession.flush()
        except IntegrityError:
            transaction.doom()
            flash(_('Username already activated'))
            return redirect(self.mount_point)

        reg.user = u
        reg.password = '******'
        reg.activated = datetime.now()

        hooks = config['hooks'].get('registration.after_activation', [])
        for func in hooks:
            func(reg, u)

        flash(_('Account succesfully activated'))
        return redirect('/')

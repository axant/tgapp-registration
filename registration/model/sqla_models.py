import json
from tg import url
from tg.decorators import cached_property

import transaction, string, random, time, hashlib

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import backref, relation, deferred

from registration.model import DBSession
from tgext.pluggable import app_model, primary_key
from tgext.pluggable.utils import mount_point

from datetime import datetime, timedelta
from registration.model.dal_interface import IRegistration, DalIntegrityError

DeclarativeBase = declarative_base()


class Registration(DeclarativeBase):
    __tablename__ = 'registration_registration'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    time = Column(DateTime, default=datetime.now)
    user_name = Column(Unicode(255), nullable=False)
    email_address = Column(Unicode(255), nullable=False)
    password = Column(Unicode(255), nullable=False)
    code = Column(Unicode(255), nullable=False)
    activated = Column(DateTime)

    user_id = Column(Integer, ForeignKey(primary_key(app_model.User)))
    user = relation(app_model.User, uselist=False, backref=backref('registration', uselist=False, cascade='all'))

    @property
    def dictified(self):
        return vars(self)

    @cached_property
    def activation_link(self):
        return url(mount_point('registration') + '/activate',
                   params=dict(code=self.code),
                   qualified=True)

    @classmethod
    def generate_code(cls, email):
        code_space = string.ascii_letters + string.digits
        def _generate_code_impl():
            base = ''.join(random.sample(code_space, 8))
            base += email
            base += str(time.time())
            return hashlib.sha1(base.encode('utf-8')).hexdigest()
        code = _generate_code_impl()
        while DBSession.query(cls).filter_by(code=code).first():
            code = _generate_code_impl()
        return code

    @classmethod
    def clear_expired(cls):
        for expired_reg in DBSession.query(cls).filter_by(activated=None)\
                                      .filter(Registration.time<datetime.now()-timedelta(days=2)):
            DBSession.delete(expired_reg)

    @classmethod
    def get_inactive(cls, code):
        return DBSession.query(Registration).filter_by(activated=None)\
                                            .filter_by(code=code).first()


class SqlaRegistration(IRegistration):

    def new(self, **kw):
        new_reg = Registration()
        new_reg.email_address = kw['email_address']
        new_reg.user_name = kw['user_name']
        new_reg.password = kw['password']
        new_reg.code = Registration.generate_code(kw['email_address'])
        DBSession.add(new_reg)
        DBSession.flush()
        return new_reg

    def clear_expired(self):
        return Registration.clear_expired()

    def out_of_uow_flush(self, entity=None):
        DBSession.add(entity)
        try:
            DBSession.flush()
        except IntegrityError:
            transaction.doom()
            raise DalIntegrityError
        return entity

    def by_email(self, email):
        return DBSession.query(Registration).filter_by(email_address=email).first()

    def get_inactive(self, code):
        return Registration.get_inactive(code)

    def pending_activation(self):
        return DBSession.query(Registration).filter(Registration.activated==None)

    def get_user_by_email(self, email_address):
        return app_model.DBSession.query(app_model.User).filter_by(email_address=email_address).first()

    def get_user_by_user_name(self, user_name):
        return app_model.DBSession.query(app_model.User).filter_by(user_name=user_name).first()

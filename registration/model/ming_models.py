from datetime import datetime, timedelta
import time
import hashlib
import random
import string
from bson import ObjectId
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty
from ming.odm.declarative import MappedClass
from tg import url
from tg.caching import cached_property
from tgext.pluggable import app_model
from tgext.pluggable.utils import mount_point
from registration.model import DBSession
from registration.model.dal_interface import IRegistration, DalIntegrityError
from pymongo.errors import DuplicateKeyError


class Registration(MappedClass):
    class __mongometa__:
        session = DBSession
        name = 'registration_registration'
        indexes = [(('activated', ), ('code', ))]
        
    _id = FieldProperty(s.ObjectId)
    time = FieldProperty(s.DateTime, if_missing=datetime.now)
    user_name = FieldProperty(s.String, required=True)
    email_address = FieldProperty(s.String, required=True, index=True)
    password = FieldProperty(s.String, required=True)
    code = FieldProperty(s.String)
    activated = FieldProperty(s.DateTime)
    extras = FieldProperty(s.Anything)

    user_id = ForeignIdProperty(app_model.User)

    @property
    def dictified(self):
        return dict(time=self.time, user_name=self.user_name, email_address=self.email_address,
                    code=self.code, activated=self.activated, user_id=self.user_id,
                    activation_link=self.activation_link)

    @cached_property
    def user(self):
        return app_model.User.get(ObjectId(self.user_id))

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
        while cls.query.find({'code': code}).first():
            code = _generate_code_impl()
        return code

    @classmethod
    def clear_expired(cls):
        for expired_reg in cls.query.find({'activated': None, 'time': {'$lte': datetime.now()-timedelta(days=2)}}):
            expired_reg.delete()

    @classmethod
    def get_inactive(cls, code):
        return cls.query.find(dict(activated=None, code=code)).first()


class MingRegistration(IRegistration):

    def new(self, **kw):
        new_reg = Registration(**kw)

        new_reg.code = Registration.generate_code(kw['email_address'])
        DBSession.flush()
        return new_reg

    def clear_expired(self):
        return Registration.clear_expired()

    def out_of_uow_flush(self, entity):
        try:
            DBSession.flush()
        except DuplicateKeyError:
            DBSession.clear()
            raise DalIntegrityError
        return entity

    def by_email(self, email):
        return Registration.query.find({'email_address': email}).first()

    def get_inactive(self, code):
        return Registration.get_inactive(code)

    def pending_activation(self):
        return Registration.query.find({'activated': None})

    def get_user_by_email(self, email_address):
        return app_model.User.query.find({'email_address': email_address}).first()

    def get_user_by_user_name(self, user_name):
        return app_model.User.query.find({'user_name': user_name}).first()

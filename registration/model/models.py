from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import backref, relation

from registration.model import DeclarativeBase, DBSession
from tgext.pluggable import app_model, primary_key

from datetime import datetime, timedelta
import string, random, time, hashlib

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

    @classmethod
    def generate_code(cls, email):
        code_space = string.ascii_letters + string.digits
        def _generate_code_impl():
            base = ''.join(random.sample(code_space, 8))
            base += email
            base += str(time.time())
            return hashlib.sha1(base).hexdigest()
        code = _generate_code_impl()
        while DBSession.query(cls).filter_by(code=code).first():
            code = _generate_code_impl()
        return code

    @classmethod
    def clear_expired(cls):
        expired = DBSession.query(cls).filter_by(activated=None)\
                                      .filter(Registration.time<datetime.now()-timedelta(7)).delete()

    @classmethod
    def get_inactive(cls, email_address, code):
        return DBSession.query(Registration).filter_by(activated=None)\
                                            .filter_by(code=code)\
                                            .filter_by(email_address=email_address).first()

import bson
from webtest import TestApp
import transaction

from tg import AppConfig, config
from tg.configuration import milestones
from tg.configuration.auth import TGAuthMetadata
from tgext.pluggable import plug, app_model

from sqlalchemy import Integer, Column, Unicode, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy import event

import ming
from ming import Session
from ming.odm import ThreadLocalODMSession
from ming.odm.declarative import MappedClass
from ming.odm import FieldProperty
from ming import schema as s


class FakeAppPackage(object):
    __file__ = __file__
    __name__ = 'tests'

    class lib(object):
        class helpers(object):
            pass
        helpers = helpers()

        class app_globals(object):
            class Globals():
                pass
        app_globals = app_globals()


class FakeSQLAModel(object):
    def __init__(self):
        self.DeclarativeBase = declarative_base()
        self.DBSession = scoped_session(sessionmaker(autoflush=True, autocommit=False,
                                                     extension=ZopeTransactionExtension()))

        class User(self.DeclarativeBase):
            __tablename__ = 'tg_user'

            user_id = Column(Integer, autoincrement=True, primary_key=True)
            user_name = Column(Unicode(16), unique=True, nullable=False)
            email_address = Column(Unicode(255), unique=True, nullable=False)
            display_name = Column(Unicode(255))
            password = Column(Unicode(255), nullable=False)

        self.User = User

    def init_model(self, engine):
        self.DBSession.configure(bind=engine)
        self.DeclarativeBase.metadata.drop_all(engine)
        self.DeclarativeBase.metadata.create_all(bind=engine)


class FakeMingModel(object):
    def __init__(self):
        self.ming_session = Session()
        self.DBSession = ThreadLocalODMSession(self.ming_session)

        class User(MappedClass):
            class __mongometa__:
                session = self.DBSession
                name = 'tg_user'
                unique_indexes = [('user_name',), ('email_address',)]

            _id = FieldProperty(s.ObjectId)
            user_name = FieldProperty(s.String)
            email_address = FieldProperty(s.String)
            display_name = FieldProperty(s.String)
            password = FieldProperty(s.String)

        self.User = User

    def init_model(self, datastore):
        self.ming_session.bind = datastore

        try:
            # On MIM drop all data
            datastore.conn.drop_all()
        except TypeError:
            # On MongoDB drop database
            datastore.conn.drop_database(datastore.db)

        ming.odm.Mapper.compile_all()
        for mapper in ming.odm.Mapper.all_mappers():
            self.ming_session.ensure_indexes(mapper.collection)


class FakeUser(bson.ObjectId):
    """
    Fake user that emulates an users without the need to actually
    query it from the database, it is able to trick sprox when
    resolving relations to the blog post Author.
    """
    def __int__(self):
        return 1

    def __getattr__(self, item):
        if item == 'user_id':
            return 1
        elif item == '_id':
            return self
        return super(FakeUser, self).__getattr__(item)


class TestAuthMetadata(TGAuthMetadata):
    def authenticate(self, environ, identity):
        return 'user'

    def get_user(self, identity, userid):
        if userid:
            return FakeUser()

    def get_groups(self, identity, userid):
        if userid:
            return ['managers']
        return []

    def get_permissions(self, identity, userid):
        if userid:
            return ['registration-admin']
        return []

def configure_app(using):
    # Simulate starting configuration process from scratch
    milestones._reset_all()

    app_cfg = AppConfig(minimal=True)
    app_cfg.renderers = ['kajiki']
    app_cfg.default_renderer = 'kajiki'
    app_cfg.use_dotted_templatenames = True
    app_cfg.package = FakeAppPackage()
    app_cfg.use_toscawidgets2 = True
    app_cfg.sa_auth.authmetadata = TestAuthMetadata()
    app_cfg['beaker.session.secret'] = app_cfg['session.secret'] = 'SECRET'
    app_cfg.auth_backend = 'ming'
    app_cfg['mail.debugmailer'] = 'dummy'


    if using == 'sqlalchemy':
        app_cfg.package.model = FakeSQLAModel()
        app_cfg.use_sqlalchemy = True
        app_cfg['sqlalchemy.url'] = 'sqlite://'
        app_cfg.use_transaction_manager = True
    elif using == 'ming':
        app_cfg.package.model = FakeMingModel()
        app_cfg.use_ming = True
        app_cfg['ming.url'] = 'mim:///testregistration'
    else:
        raise ValueError('Unsupported backend')

    app_cfg.model = app_cfg.package.model
    app_cfg.DBSession = app_cfg.package.model.DBSession

    # CUSTOM registration options
    app_cfg['registration.email_sender'] = 'reg@email.it'



    from registration.lib import send_email, get_form

    # Guarantee that the same form is used between multiple
    # configurations of TGApps. Otherwise the validated
    # form would be different from the displayed one.
    plug_args = {}
    if '_pluggable_registration_config' in config:
        plug_args['form_instance'] = get_form()

    plug(app_cfg, 'tgext.mailer', plug_bootstrap=True, debugmailer='dummy')
    plug(app_cfg, 'registration', plug_bootstrap=False, **plug_args)
    return app_cfg


def create_app(app_config, auth=False):
    from registration import lib
    lib.SENT_EMAILS = []

    app = app_config.make_wsgi_app(skip_authentication=True)
    if auth:
        return TestApp(app, extra_environ=dict(REMOTE_USER='user'))
    else:
        return TestApp(app)


def flush_db_changes():
    app_model.DBSession.flush()
    transaction.commit()

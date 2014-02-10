# -*- coding: utf-8 -*-
from tg import config
from tgext.pluggable import PluggableSession

DBSession = PluggableSession()

Registration = None


def init_model(app_session):
    DBSession.configure(app_session)


def patch_global_registration():
    global Registration
    use_sqlalchemy = config.get('use_sqlalchemy')
    if use_sqlalchemy:
        from .sqla_models import Registration
    else:
        from .ming_models import Registration

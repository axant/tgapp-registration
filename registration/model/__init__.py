# -*- coding: utf-8 -*-
from tgext.pluggable import PluggableSession

DBSession = PluggableSession()


def init_model(app_session):
    DBSession.configure(app_session)


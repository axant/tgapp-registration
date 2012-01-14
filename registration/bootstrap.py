# -*- coding: utf-8 -*-
"""Setup the registration application"""

from registration import model
from tgext.pluggable import app_model

def bootstrap(command, conf, vars):
    print 'Bootstrapping registration...'
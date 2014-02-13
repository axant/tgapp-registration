# -*- coding: utf-8 -*-
"""The tgapp-registration package"""

def plugme(app_config, options):
    app_config['_pluggable_registration_config'] = options
    return dict(appid='registration', global_helpers=False)
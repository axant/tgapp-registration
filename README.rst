.. image:: https://badge.fury.io/py/tgapp-registration.svg
    :target: https://badge.fury.io/py/tgapp-registration
.. image:: https://travis-ci.org/axant/tgapp-registration.svg?branch=master
    :target: https://travis-ci.org/axant/tgapp-registration
.. image:: https://coveralls.io/repos/github/axant/tgapp-registration/badge.svg?branch=master
    :target: https://coveralls.io/github/axant/tgapp-registration?branch=master

About TGApp-Registration
-------------------------

Registration is a Pluggable registration application for TurboGears2.
By default it will work with the quickstart TurboGears User model
but provides a bunch of hooks that can be used to change the registration
form and most of the registration aspects.

Registration currently supports both ``SQLAlchemy`` and ``MongoDB``
for database storage.

Registration supports both ``Turbomail`` and ``tgext.mailer`` to send emails.

Installing
-------------------------------

tgapp-registration can be installed both from pypi or from bitbucket::

    pip install tgapp-registration

should just work for most of the users

If you want to use *Turbomail* as sender install it from pypi::

    pip install turbomail

If you want to use *tgext.mailer* as sender install it from pypi or from bitbucket::

    pip install tgext.mailer

Plugging Registration
----------------------------

In your application *config/app_cfg.py* import **plug**::

    from tgext.pluggable import plug

Then at the *end of the file* call plug with registration::

    plug(base_config, 'registration')

If you use *tgext.mailer* you need to plug it::

    plug(base_config, 'tgext.mailer')

You will be able to access the registration process at
*http://localhost:8080/registration*.

Some options are available that can be set on ``.ini``
configuration file for your application.
At least one option is required to make activation emails
work:

    * **registration.email_sender** -> Outgoing mails sender address (like ``no-repy@domain.com``)

If you are using *tgext.mailer* you need to set up some configuration, check here for available options:
*https://github.com/amol-/tgext.mailer*.

If you are not using neither *TurboMail* or *tgext.mailer* a few more configuration
options must be set to make activation email work:

    * **registration.smtp_host** -> SMTP server to use to send emails

    * **registration.smtp_login** -> Login for authentication on SMTP server

    * **registration.smtp_passwd** -> Password for authentication on SMTP server

Plugin Options
---------------------

When plugging ``tgapp-registration`` the following options
can be passed to the plug call:

    * **registration.form** -> Full python path of the form class to use for Registration form. By default *registration.lib.forms.RegistrationForm* is used.

Available Hooks
----------------------

Registration exposes some hooks to configure it's behavior,
The hooks that can be used with TurboGears2 *register_hook* are:

    * **registration.before_registration_form(arguments)** -> Runs before rendering the form. Can be used to insert preconditions to limit the registration for example just to invited users. You can fill the form inserting data into arguments, you might want to put a json serialized dictionary into arguments['extra'] that is an HiddenField in the form

    * **registration.before_registration(submitted_values)** -> Runs after form submission. Can be used to change the values submitted by the form before they are used

    * **registration.after_registration(registration, submitted_values)** -> Runs after form submission. Can be used to store eventual data that the form sent and that the Registration model doesn't support.

    * **registration.on_complete(registration, email_data)** -> Runs after registration completion before sending activation email, can be used to change outgoing email.

    * **registration.before_activation(registration, user)** -> Runs at activation before creating the user and setting the registration as active

    * **registration.after_activation(registration, user)** -> Runs after creating user, can be used to call *redirect* to redirect to a different page at registration completion.

Exposed Templates
--------------------

The templates used by registration and that can be replaced with
*tgext.pluggable.replace_template* are:

    * registration.templates.register

    * registration.templates.complete

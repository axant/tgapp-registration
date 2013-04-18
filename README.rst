About TGApp-Registration
-------------------------

Registration is a Pluggable registration application for TurboGears2.
By default it will work with the quickstart TurboGears User model
but provides a bunch of hooks that can be used to change the registration
form and most of the registration aspects.

Installing
-------------------------------

tgapp-registration can be installed both from pypi or from bitbucket::

    easy_install tgapp-registration

should just work for most of the users

Plugging Registration
----------------------------

In your application *config/app_cfg.py* import **plug**::

    from tgext.pluggable import plug

Then at the *end of the file* call plug with registration::

    plug(base_config, 'registration')

You will be able to access the registration process at
*http://localhost:8080/registration*.

Some options are available that can be set on .ini
configuration file for your application.
At least one option is required to make activation emails
work:

    * **registration.email_sender** -> Outgoing mails sender

If you are not using *TurboMail* a few more configuration
options must be set to make activation email work:

    * **registration.smtp_host** -> SMTP server to use to send emails

    * **registration.smtp_login** -> Login for authentication on SMTP server

    * **registration.smtp_passwd** -> Password for authentication on SMTP server

Available Hooks
----------------------

Registration exposes some hooks and options to configure its
aspects. The most important option is:

    * **registration.form** -> Full python path of the form class to use for Registration form. By default *registration.lib.forms.RegistrationForm* is used.

The hooks that can be used with TurboGears2 *register_hook* are:

    * **registration.before_registration(submitted_values)** -> Runs after form submission. Can be used to change the values submitted by the form before they are used

    * **registration.after_registration(registration, submitted_values)** -> Runs after form submission. Can be used to store eventual data that the form sent and that the Registration model doesn't support.

    * **registration.on_complete(email_data)** -> Runs after registration completion before sending activation email, can be used to change outgoing email.

    * **registration.before_activation(registration, user)** -> Runs at activation before creating the user and setting the registration as active

    * **registration.after_activation(registration, user)** -> Runs after creating user, can be used to call *redirect* to redirect to a different page at registration completion.

Exposed Templates
--------------------

The templates used by registration and that can be replaced with
*tgext.pluggable.replace_template* are:

    * registration.templates.register

    * registration.templates.complete

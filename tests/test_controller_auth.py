from tgext.pluggable import app_model
from .base import configure_app, create_app, flush_db_changes
from registration import lib, model
import re

find_urls = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


class RegistrationAuthControllerTests(object):
    def setup(self):
        self.app = create_app(self.app_config, True)

    def _registration_submit(self):
        resp = self.app.get('/registration')
        form = resp.form

        form['email_address'] = 'email@email.it'
        form['password_confirm'] = 'p'
        form['password'] = 'p'
        form['user_name'] = 'user1'
        form.submit()

    def test_admin(self):
        self._registration_submit()
        self._registration_submit()
        self._registration_submit()

        resp = self.app.get('/registration/admin')
        resp = resp.text

        assert resp.count('<td>email@email.it') == 3
        assert resp.count('<td>user1') == 3
        assert resp.count('<a href="http://localhost/registration/activate?code=') == 3


class TestRegistrationAuthControllerSQLA(RegistrationAuthControllerTests):
    @classmethod
    def setupClass(cls):
        cls.app_config = configure_app('sqlalchemy')


class TestRegistrationAuthControllerMing(RegistrationAuthControllerTests):
    @classmethod
    def setupClass(cls):
        cls.app_config = configure_app('ming')


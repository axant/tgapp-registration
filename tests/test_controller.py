from tgext.pluggable import app_model
from .base import configure_app, create_app, flush_db_changes
from registration import lib, model
import re

find_urls = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


class RegistrationControllerTests(object):
    def setup(self):
        self.app = create_app(self.app_config, False)

    def test_index(self):
        resp = self.app.get('/')
        assert 'HELLO' in resp.text

    def test_registration_form(self):
        resp = self.app.get('/registration')

        assert 'name="user_name"' in resp.text
        assert 'name="email_address"' in resp.text
        assert 'name="password"' in resp.text
        assert 'name="password_confirm"' in resp.text
        assert 'action="/registration/submit"' in resp.text

    def test_registration_validation(self):
        resp = self.app.get('/registration')
        form = resp.form
        assert form.action == '/registration/submit'

        form['email_address'] = 'invalid1'
        form['password_confirm'] = 'p'
        resp = form.submit()

        assert '<span id="email_address:error">Invalid email</span>' in resp.text
        assert '<span id="user_name:error">Please enter a value</span>' in resp.text
        assert '<span id="password_confirm:error">Fields do not match</span>' in resp.text
        assert '<span id="password:error">Enter a value</span>' in resp.text

    def test_registration_empty_email(self):
        resp = self.app.get('/registration')
        form = resp.form
        assert form.action == '/registration/submit'

        form['email_address'] = ''
        resp = form.submit()

        assert '<span id="email_address:error">Please enter a value</span>' in resp.text

    def test_registration_submit(self):
        resp = self.app.get('/registration')
        form = resp.form

        form['email_address'] = 'email@email.it'
        form['password_confirm'] = 'p'
        form['password'] = 'p'
        form['user_name'] = 'user1'
        resp = form.submit()
        resp = resp.follow()

        assert '<strong>An email</strong> has been sent to <strong>email@email.it</strong>' \
               ' to activate the account' in resp.text
        assert len(lib.SENT_EMAILS) == 1

    def test_registration_submit_twice(self):
        self.test_registration_submit()
        lib.SENT_EMAILS = []
        self.test_registration_submit()

    def test_registration_activate(self):
        self.test_registration_submit()

        url = find_urls.findall(lib.SENT_EMAILS[0]['body'])[0]
        resp = self.app.get(url)
        assert 'Account%20succesfully%20activated' in resp.headers['Set-Cookie']

    def test_registration_activate_twice(self):
        self.test_registration_submit()

        url = find_urls.findall(lib.SENT_EMAILS[0]['body'])[0]
        resp = self.app.get(url)
        assert 'Account%20succesfully%20activated' in resp.headers['Set-Cookie']

        resp = self.app.get(url)
        assert 'Registration%20not%20found%20or%20already%20activated' in resp.headers['Set-Cookie']

    def test_registration_duplicate_user(self):
        self.test_registration_submit()
        url = find_urls.findall(lib.SENT_EMAILS[0]['body'])[0]

        # Create user in the mean while
        user = app_model.User(email_address='email@email.it',
                              user_name='user1',
                              password='password')

        try:
            model.DBSession.add(user)
        except AttributeError:
            pass
        flush_db_changes()

        resp = self.app.get(url)
        assert 'Username%20already%20activated' in resp.headers['Set-Cookie'], resp

    def test_registration_user_existing(self):
        self.test_registration_activate()

        resp = self.app.get('/registration')
        form = resp.form
        form['email_address'] = 'email@email.it'
        form['password_confirm'] = 'p'
        form['password'] = 'p'
        form['user_name'] = 'user1'
        resp = form.submit()

        assert '<span id="email_address:error">Email address has already been taken</span>' in resp.text
        assert '<span id="user_name:error">Username already in use.</span>' in resp.text


class TestRegistrationControllerSQLA(RegistrationControllerTests):
    @classmethod
    def setupClass(cls):
        cls.app_config = configure_app('sqlalchemy')


class TestRegistrationControllerMing(RegistrationControllerTests):
    @classmethod
    def setupClass(cls):
        cls.app_config = configure_app('ming')


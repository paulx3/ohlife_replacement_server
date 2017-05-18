'''

@author: wanzeyu

@contact: wan.zeyu@outlook.com

@file: test.py

@time: 2017/5/3 17:48

@desc: test suite

'''
import json
import unittest

from flask_testing import TestCase

from server.helpers import get_credential, back_db
from server.server import db, User, Entries, create_app, app


class testCreation(TestCase):
    """
    db test initiation
    """

    def create_app(self):
        """
        create app
        Returns: flask app object

        """
        self.app = create_app("sqlite:///", True)
        self.app.testing = True
        self.app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        return self.app

    def setUp(self):
        """
        create db
        """
        db.create_all()

    def tearDown(self):
        """
        delete all 
        """
        db.session.remove()
        db.drop_all()

    @staticmethod
    def get_user():
        """
        generate user object
        Returns: user object

        """
        user = User("test_account", "test_password", "test@test.com")
        return user

    @staticmethod
    def get_entry_text():
        """
        generate test text
        :return: string
        """
        text = "I want to change the world."
        return text


class testUserCRUD(testCreation):
    """
    test user table CRUD
    """

    def test_user_add(self):
        """
        test add user
        """
        user = self.get_user()
        db.session.add(user)
        db.session.commit()
        assert user in db.session

    def test_user_delete(self):
        """
        test delete user
        """
        user = self.get_user()
        db.session.add(user)
        db.session.commit()
        db.session.delete(user)
        db.session.commit()
        assert user not in db.session


class testEntriesCRUD(testCreation):
    """
    test entries table CRUD
    """

    def test_entries_add(self):
        """
        test diary add
        """
        user = self.get_user()
        db.session.add(user)
        text = self.get_entry_text()
        entry = Entries(text, user.user_id)
        db.session.add(entry)
        db.session.commit()
        assert entry in db.session

    def test_entries_delete(self):
        """
        test diary delete
        """
        user = self.get_user()
        db.session.add(user)
        text = self.get_entry_text()
        entry = Entries(text, user.user_id)
        db.session.add(entry)
        db.session.commit()
        db.session.delete(entry)
        db.session.commit()
        assert entry not in db.session


class testWebApi(unittest.TestCase):
    """
    API test initiation
    """

    @staticmethod
    def get_mock_user_password():
        return "test_password"

    @staticmethod
    def get_user():
        """
        generate user object
        Returns: user object

        """
        user = User("test_account", testWebApi.get_mock_user_password(), "test@test.com")
        return user

    def assert_flashes(self, expected_message, expected_category='message'):
        """
        assert flashes in response
        :param expected_message: 
        :param expected_category: 
        """
        with self.client.session_transaction() as session:
            try:
                category, message = session['_flashes'][0]
            except KeyError:
                raise AssertionError('nothing flashed')
            assert expected_message in message
            assert expected_category == category

    def setUp(self):
        # instantiate a flask test client
        app.config["TESTING"] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.client = app.test_client()
        # create the database objects
        app.app_context().push()
        db.create_all()
        # add some fixtures to the database
        self.user = self.get_user()
        db.session.add(self.user)
        db.session.commit()

    # this method is run after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()


class testUserApi(testWebApi):
    """
    test user API
    """

    def login(self, email, password):
        return self.client.post('/login', data=dict(email=email,
                                                    password=password))

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def auth(self, username, password):
        return self.client.post('/auth', data=json.dumps(dict(username=username, password=password)),
                                content_type='application/json')

    def test_user_login_wrong_password(self):
        """
        test user login using wrong password
        """
        response = self.login(self.user.email, "test_wrong")
        assert b"Wrong Password" == response.data

    def test_user_login_wrong_username(self):
        """
        test user login using wrong 
        """
        response = self.login("test_wrong", self.get_mock_user_password())
        assert b"Wrong Username" == response.data

    def test_user_login(self):
        """
        test user login using wrong 
        """
        response = self.login(self.user.email, self.get_mock_user_password())
        self.assertEqual(response.status_code, 302)
        assert '/admin' in response.location

    def test_jwt_auth_json(self):
        """
        test jwt auth
        :return: jwt token
        """
        response = self.auth(self.user.username, self.get_mock_user_password())
        data = json.loads(bytes.decode(response.data))
        assert type(data) == dict

    def test_register(self):
        """
        test user register
        """
        pass


class testHelpers(unittest.TestCase):
    """
    test ohlife helpers
    """

    # def test_customized_text_generation(self):
    #     """
    #     test customized text generation
    #     """
    #     text = get_replacable("2017-03-22")
    #     assert text == "Today is a test"

    # def test_template_render(self):
    #     """
    #     test Ninja render
    #     """
    #     context = {
    #         "data": "",
    #         "time_ago": "test_time_ago",
    #         "replacable": "replacable_text",
    #         "save_key": "test_save_key",
    #         "name": "test user",
    #     }
    #     html_rendered = render("sender.html", context)
    #     assert "test user" in html_rendered

    def test_backdb(self):
        """
        test database backup
        """
        assert 0 == back_db()

    def test_get_credential(self):
        """
        test get credential
        """
        credential = get_credential()
        assert type(credential) == dict

    def test_send_email(self):
        """
        test send emal
        :return: 
        """
        pass
if __name__ == '__main__':
    unittest.main()

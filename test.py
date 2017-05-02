'''

@author: wanzeyu

@contact: wan.zeyu@outlook.com

@file: test.py

@time: 2017/4/7 10:55

@desc: test suite

'''
import unittest

from flask_testing import TestCase

from server.server import db, User, create_app, Entries


class testCreation(TestCase):
    """
    test Flask creation
    """

    def create_app(self):
        """
        create app
        Returns: flask app object

        """
        return create_app("sqlite:///", True)

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


class testUserApi(testCreation):
    """
    test user API
    """

    def test_user_login(self):
        """
        test user login
        """
        pass

    def testRegister(self):
        """
        test user register
        """
        pass

    def testLogout(self):
        """
        test user logout
        """
        pass


class testGetCredential(testCreation):
    """
    test get credential
    """
    pass


class testBackDB(testCreation):
    """
    test database backup
    """
    pass


class testSendEmail(testCreation):
    def testCustomizedTextGeneration(self):
        """
        test customized text generation
        """
        pass

    def testTemplateRender(self):
        """
        test Ninja render
        """
        pass


if __name__ == '__main__':
    unittest.main()

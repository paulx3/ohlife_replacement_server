'''

@author: wanzeyu

@contact: wan.zeyu@outlook.com

@file: test.py

@time: 2017/4/7 10:55

@desc: test suite

'''
import random
import unittest

from elizabeth import Personal
from flask_testing import TestCase

from server import db, User, create_app


class testCreation(TestCase):
    def create_app(self):
        return create_app("sqlite:///")

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class testUserCRUDTest(testCreation):
    def get_user(self):
        person = Personal('en')
        user = User(person.full_name(), str(random.randint(0, 99)), person.email())
        return user

    def test_user_add(self):
        self.user = self.get_user()
        db.session.add(self.user)
        db.session.commit()
        assert self.user in db.session

    # def test_user_delete(self):
    #     db.session.remove(self.user)
    #     db.session.commit()
    #     assert self.user not in db.session

if __name__ == '__main__':
    unittest.main()

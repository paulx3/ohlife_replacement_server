'''

@author: wanzeyu

@contact: wan.zeyu@outlook.com

@file: test.py

@time: 2017/4/7 10:55

@desc: test suite

'''
import unittest

from flask_testing import TestCase

from server.server import db, User, create_app


class testCreation(TestCase):
    """
    测试flask创建
    """

    def create_app(self):
        """
        创建app
        Returns: flask app对象

        """
        return create_app("sqlite:///")

    def setUp(self):
        """
        创建数据库
        """
        db.create_all()

    def tearDown(self):
        """
        删除测试数据
        """
        db.session.remove()
        db.drop_all()


class testUserCRUDTest(testCreation):
    """
    测试user表的增删改查
    """

    def get_user(self):
        """
        生成用户测试数据
        Returns: 用户对象

        """
        user = User("test_account", "test_password", "test@test.com")
        return user

    def test_user_add(self):
        """
        测试添加用户
        """
        user = self.get_user()
        db.session.add(user)
        db.session.commit()
        assert user in db.session

    def test_user_delete(self):
        """
        测试删除用户
        """
        user = self.get_user()
        db.session.add(user)
        db.session.remove()
        db.session.commit()
        assert user not in db.session


if __name__ == '__main__':
    unittest.main()

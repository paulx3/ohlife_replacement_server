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
    测试flask创建
    """

    def create_app(self):
        """
        创建app
        Returns: flask app对象

        """
        return create_app("sqlite:///", True)

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

    @staticmethod
    def get_user():
        """
        生成用户测试数据
        Returns: 用户对象

        """
        user = User("test_account", "test_password", "test@test.com")
        return user

    @staticmethod
    def get_entry_text():
        """
        生成日志测试文本
        :return: string
        """
        text = "I want to change the world."
        return text


class testUserCRUD(testCreation):
    """
    测试user表的增删改查
    """

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
        db.session.commit()
        db.session.delete(user)
        db.session.commit()
        assert user not in db.session


class testEntriesCRUD(testCreation):
    """
    测试entries
    """

    def test_entries_add(self):
        """
        测试日志添加
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
        测试日志删除
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


if __name__ == '__main__':
    unittest.main()

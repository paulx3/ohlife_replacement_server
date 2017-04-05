'''

@author: wanzeyu

@contact: wan.zeyu@outlook.com

@file: test.py

@time: 2017/3/30 11:32

@desc: test

'''
import os
from server import *
import jinja2


def render(template_name, context):
    """
    直接渲染本地template
    :param template_name: 模板名
    :param context: 环境dict
    :return: 渲染出来的html
    """
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader('./templates')
    ).get_template(template_name).render(context)


# user = User(str(uuid.uuid1()), "test", "qweqweqwe", "test@test.com")
# db.session.add(user)
# db.session.commit()
# user = User.query.filter_by(email="test@test.com").first()
# print(user.username)
def func(x):
    return x + 1

def test_answer():
    assert func(3) == 5
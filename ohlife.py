'''

@author: wanzeyu

@contact: wan.zeyu@outlook.com

@file: userTest.py

@time: 2017/3/27 14:11

@desc: Ohlife 定时服务

'''

import arrow

from sqlalchemy.sql.expression import func
from helpers import get_replacable, render, send_local_mail
from server import Entries, User
from server import save_signer

# file_dir = "/home/ubuntu/ohlife-replacement/ohlife/"
file_dir = ""


def send_mail(users_text_list):
    """
    读取用户列表，逐个发送邮件
    :param users_text_list: 
    """
    today = arrow.now().format('YYYY-MM-DD')
    subject = u"今天是 %s - 你今天过得怎么样啊?" % today
    for user in users_text_list:
        time_ago = users_text_list[user][0]
        data = users_text_list[user][1]
        context = {
            "data": data,
            "time_ago": time_ago,
            "replacable": get_replacable(today),
            "save_key": bytes.decode(save_signer.sign(user.session_id)),
            "name": user.username
        }
        html_rendered = render("sender.html", context)
        print(html_rendered)
        # send_local_mail(['Paul <xzycxy@126.com>'], 'OhLife<141db7d5da23b3e7909b@cloudmailin.net>', subject,
        #                 html_rendered, [])


def get_entry(users):
    """
    获得对应用户的text
    :param users:用户对象列表 
    :return: 返回{user_id:(time_ago,text)}
    """
    user_text_list = {}
    # 计算时间差
    last_year = arrow.now().replace(years=-1).format('YYYY-MM-DD')
    last_month = arrow.now().replace(months=-1).format('YYYY-MM-DD')
    last_week = arrow.now().replace(weeks=-1).format('YYYY-MM-DD')

    # 循环查找每个user的text
    for user in users:
        current_id = user.user_id
        result = Entries.query.filter_by(time=last_year, user_id=current_id).first()
        if result:
            print(u"一年", result.text)
            user_text_list[user] = (u"一年", result.text)

        result = Entries.query.filter_by(time=last_month, user_id=current_id).first()
        if result:
            print(u"一个月", result.text)
            user_text_list[user] = (u"一个月", result.text)

            result = Entries.query.filter_by(time=last_week, user_id=current_id).first()
        if result:
            print(u"一周", result.text)
            user_text_list[user] = (u"一周", result.text)

        result = Entries.query.filter_by(user_id=current_id).order_by(func.random()).first()
        if result:
            num_days_ago = (arrow.now() - arrow.get(result.time)).days - 1
            if num_days_ago <= 0:
                num_days_ago = "今"
                print(u"%s天" % str(num_days_ago), result.text)
                user_text_list[user] = (u"%s天" % str(num_days_ago), result.text)
            else:
                print(u"%s 天" % str(num_days_ago), result.text)
                user_text_list[user] = (u"%s 天" % str(num_days_ago), result.text)

    return user_text_list


def get_users():
    """
    获得所有user对象
    """
    users = User.query.all()
    return users


def main():
    """
    程序入口
    """
    users = get_users()
    users_text_list = get_entry(users)
    send_mail(users_text_list)


if __name__ == '__main__':
    main()

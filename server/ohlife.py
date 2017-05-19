'''

@author: wanzeyu

@contact: wan.zeyu@outlook.com

@file: userTest.py

@time: 2017/3/27 14:11

@desc: Ohlife Send Timer

'''

import arrow
from sqlalchemy.sql.expression import func

from helpers import get_replacable, render, get_credential, gnu_translations
from server import Entries, User, create_app
from server import save_signer

# file_dir = "/home/ubuntu/ohlife-replacement/ohlife/"
file_dir = ""

gnu_translations.install()


def send_mail(users_text_list):
    """
    traverse user list and send emails
    :param users_text_list: 
    """
    credential = get_credential()
    today = arrow.now().format('YYYY-MM-DD')
    # subject = u"今天是 %s - 你今天过得怎么样啊?" % today
    subject = gnu_translations.gettext("Today is %s - How's everything going ?") % today
    for user in users_text_list:
        time_ago = users_text_list[user][0]
        data = users_text_list[user][1]
        replacable = get_replacable(today)
        context = {
            "data": data,
            "time_ago": time_ago,
            "replacable": replacable,
            "save_key": bytes.decode(save_signer.sign(user.session_id)),
            "name": user.username,
        }
        html_rendered = render("sender.html", context)
        print(html_rendered)
        receiver = user.username + "<" + user.email + ">"
        sender = "OhLife<" + credential["mail_server"] + ">"
        # send_local_mail([receiver], sender, subject, html_rendered, [])
        # send_local_mail(mail_to=[receiver], mail_from=sender, subject=subject,
        #                 text=html_rendered, files=[], username=credential["smtp_username"]
        #                 , password=credential["smtp_password"], server=credential["smtp_server"])


def get_entry(users):
    """
    get corresponding history entries for each user
    :param users:user object list
    :return: return {user_id:(time_ago,text)}
    """
    user_text_list = {}
    # calculate time gap
    last_year = arrow.now().replace(years=-1).format('YYYY-MM-DD')
    last_month = arrow.now().replace(months=-1).format('YYYY-MM-DD')
    last_week = arrow.now().replace(weeks=-1).format('YYYY-MM-DD')

    # search for history entries for each user
    for user in users:
        current_id = user.user_id
        result = Entries.query.filter_by(time=last_year, user_id=current_id).first()
        if result:
            print(u"一年", result.text)
            user_text_list[user] = (gnu_translations.gettext("A year"), result.text)

        result = Entries.query.filter_by(time=last_month, user_id=current_id).first()
        if result:
            print(u"一个月", result.text)
            user_text_list[user] = (gnu_translations.gettext("A month"), result.text)

            result = Entries.query.filter_by(time=last_week, user_id=current_id).first()
        if result:
            print(u"一周", result.text)
            user_text_list[user] = (gnu_translations.gettext("A week"), result.text)

        result = Entries.query.filter_by(user_id=current_id).order_by(func.random()).first()
        if result:
            num_days_ago = (arrow.now() - arrow.get(result.time)).days - 1
            if num_days_ago <= 0:
                num_days_ago = gnu_translations.gettext("Today")
                print(u"%s天" % str(num_days_ago), result.text)
                # user_text_list[user] = (u"%s天" % str(num_days_ago), result.text)
                user_text_list[user] = (num_days_ago, result.text)
            else:
                # print(u"%s 天" % str(num_days_ago), result.text)
                # user_text_list[user] = (u"%s 天" % str(num_days_ago), result.text)
                user_text_list[user] = ((str(num_days_ago) + gnu_translations.gettext("days")), result.text)

    return user_text_list


def get_users():
    """
    get all user objects
    """
    users = User.query.all()
    return users


def main():
    """
    entry point for this program
    """
    create_app("sqlite:///./dbdir/ohlife.db", False).app_context().push()
    users = get_users()
    users_text_list = get_entry(users)
    send_mail(users_text_list)


if __name__ == '__main__':
    main()

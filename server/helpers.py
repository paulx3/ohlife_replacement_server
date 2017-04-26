'''

@author: wanzeyu

@contact: wan.zeyu@outlook.com

@file: helpers.py

@time: 2017/4/14 18:27

@desc: 工具类

'''
import os
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

import boto3
import jinja2

from server.helpers import get_credential

file_dir = ""


def get_replacable(date):
    """
    读取配置文件，在不同的日期返回不同的问候语
    :param date: 
    :return: string
    """
    config = open(file_dir + "config", "r", encoding="utf8")
    for line in config:
        temp = line.split("\t")
        if (date == temp[0].strip()):
            return temp[1].strip();
    return """今天，你的心情好吗？<br>心情不错，还是另有心事呢？"""


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


def send_local_mail(mail_to, mail_from, subject, text, files, server="localhost"):
    """
    通过本地服务器发送邮件
    :param mail_to: 收件人
    :param mail_from: 发件人
    :param subject: 主题
    :param text: 内容
    :param files: 文件
    :param server: 邮件服务器地址
    """
    assert type(mail_to) == list
    assert type(files) == list

    print(mail_to)
    print(mail_from)
    return
    msg = MIMEMultipart()
    msg['From'] = mail_from
    msg['To'] = COMMASPACE.join(mail_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    # 如果 text 是html，则需要设置 _subtype='html'
    # 默认情况下 _subtype='plain'，即纯文本
    # msg.attach(MIMEText(text, _subtype='html', _charset='utf-8'))
    msg.attach(MIMEText(text, _subtype='html', _charset='utf-8'))

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(f, "rb").read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
                        % os.path.basename(f))
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(mail_from, mail_to, msg.as_string())
    smtp.close()


def get_credential():
    """
    从文件读取credential
    :return: 返回credential dict
    """
    credential = {}
    with open("credential", "r", encoding="utf8") as credentialFile:
        for line in credentialFile:
            items = line.split(":")
            credential[items[0].strip()] = items[1].strip()
    return credential


def back_db():
    """
    备份数据库到Amazon S3
    """
    credential = get_credential()
    my_session = boto3.session.Session(aws_access_key_id=credential["aws_access_key_id"],
                                       aws_secret_access_key=credential["aws_secret_access_key"])
    s3 = my_session.resource("s3")
    for bucket in s3.buckets.all():
        print(bucket.name)

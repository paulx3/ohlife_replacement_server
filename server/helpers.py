'''

@author: wanzeyu

@contact: wan.zeyu@outlook.com

@file: helpers.py

@time: 2017/4/14 18:27

@desc: Utils

'''
import gettext
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

import boto3
import jinja2

dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"

# read config
credential = {}
with open(dir_path + "config.cfg", "r", encoding="utf8") as credentialFile:
    for line in credentialFile:
        items = line.split(":")
        credential[items[0].strip()] = items[1].strip()

try:
    gnu_translations = gettext.translation(
        domain="ohlife",
        localedir=dir_path + "locale/",
        languages=[credential["locale"]]
    )
except FileNotFoundError:
    print("Custom translation file not found.Using default locale")
    gnu_translations = gettext.translation(
        domain="ohlife",
        localedir=dir_path + "locale/",
        languages=[credential["locale"]]
    )

gnu_translations.install()


def get_replacable(date):
    """
    Read replacement file and return different greeting text according to time
    :param date: 
    :return: string
    """
    with open(dir_path + "replacement", "r", encoding="utf8") as config:
        for line in config:
            temp = line.split("\t")
            if date == temp[0].strip():
                return temp[1].strip()
        default_text = gnu_translations.gettext("How are you doing today?<br>Is it good or do you have worries?")
        return default_text


def render(template_name, context):
    """
    render local template
    :param template_name: template name
    :param context: context dict
    :return: rendered output html
    """
    env = jinja2.Environment(
        extensions=['jinja2.ext.i18n'],
        loader=jinja2.FileSystemLoader(dir_path + './templates')
    )
    env.install_gettext_translations(gnu_translations, newstyle=True)
    template = env.get_template(template_name)
    return template.render(context)


def send_local_mail(mail_to, mail_from, subject, text, files, username=None, password=None, server="localhost"):
    """
    send email through SMTP server
    :param mail_to: receiver
    :param mail_from: sender
    :param subject: subject
    :param text: content
    :param files: attachments
    :param username: smtp username
    :param password: smtp password
    :param server: SMTP server addreess
    """
    assert type(mail_to) == list
    assert type(files) == list

    print(mail_to)
    print(mail_from)
    msg = MIMEMultipart()
    msg['From'] = mail_from
    msg['To'] = COMMASPACE.join(mail_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    # if text is html ,set _subtype='html'
    # By default, _subtype='plain'
    # msg.attach(MIMEText(text, _subtype='html', _charset='utf-8'))
    msg.attach(MIMEText(text, _subtype='html', _charset='utf-8'))

    for f in files:  # pragma: no cover
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(f, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
                        % os.path.basename(f))
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    if username is not None and password is not None:
        smtp.login(username, password)
    smtp.sendmail(mail_from, mail_to, msg.as_string())
    smtp.close()


def get_credential():
    """
    read credential from file
    :return: return credential dict
    """
    credential = {}
    with open(dir_path + "config.cfg", "r", encoding="utf8") as credentialFile:
        for line in credentialFile:
            items = line.split(":")
            credential[items[0].strip()] = items[1].strip()
    return credential


def back_db():
    """
    backup database to Amazon S3
    """
    credential = get_credential()
    if "aws_access_key_id" in credential and "aws_secret_access_key" in credential:  # pragma: no cover
        my_session = boto3.session.Session(aws_access_key_id=credential["aws_access_key_id"],
                                           aws_secret_access_key=credential["aws_secret_access_key"])
        s3 = my_session.resource("s3")
        for bucket in s3.buckets.all():
            print(bucket.name)
        return 1
    else:
        return 0

import smtplib
import sqlite3
import arrow
import gzip
from email_credentials import email_credentials
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.encoders import encode_base64


def send_mail(subject, body, attachment=None):
    mailhost, fromaddr, replytoaddr, toaddrs, credentials = email_credentials()
    username, password = credentials
    msg = MIMEMultipart()
    msg['Subject'] = Header(subject)
    msg.attach(MIMEText(body))
    if attachment is not None:
        payload, filename = attachment
        part = MIMEBase('application', "octet-stream")
        part.set_payload(payload)
        encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % filename)
        msg.attach(part)
    server = smtplib.SMTP(mailhost)
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddr, toaddrs, msg.as_string())
    server.quit()


def get_attachment():
    with sqlite3.connect('ohlife.db') as db:
        cur = db.execute('select day, entry from entries order by day')
        result = cur.fetchall()
    psv = 'day|entry\n'
    psv += '\n'.join('%s|"%s"' % (day, entry) for day, entry in result)
    compressed_psv = gzip.compress(psv.encode('utf-8'))
    filename = 'ohlife_%s.psv.gz' % arrow.now().format('YYYYMMDD')
    return compressed_psv, filename


def main():
    subject = 'ohlife entries as of %s' % arrow.now().format('YYYYMMDD')
    body = 'See attachment'
    send_mail(subject, body, get_attachment())

if __name__ == '__main__':
    main()
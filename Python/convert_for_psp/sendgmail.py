# -*- coding: utf-8 -*-
import smtplib
import email
from email.MIMEText import MIMEText

def create_message(from_addr, to_addr, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Date'] = email.utils.formatdate()
    return msg

def send_via_gmail(from_addr, to_addr, msg, password):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(from_addr, password)
    s.sendmail(from_addr, [to_addr], msg.as_string())
    s.close()

if __name__ == '__main__':
    from_addr = '***@***'
    to_addr = '***@***'
    msg = create_message(from_addr, to_addr, 'test subject', 'test body')
    password = raw_input(u'password? >>>')
    send_via_gmail(from_addr, to_addr, msg, password)
    print msg
    print
    print u'End.'

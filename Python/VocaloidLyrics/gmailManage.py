# coding:utf-8

import smtplib
from email.MIMEText import MIMEText
from email.Header import Header

class Gmail():
    def __init__(self, GmailId, GmailPW):
        self.GmailId = GmailId
        self.GmailPW = GmailPW
    
    def createMessage(self, toAddr, subject, body):
        body = body.encode('iso-2022-jp')
        self.msg = MIMEText(body, _charset='iso-2022-jp')
        self.msg['subject'] = Header(subject, 'iso-2022-jp')
        self.msg['From'] = self.GmailId
        self.msg['To'] = toAddr

    def send(self):
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.login(self.GmailId, self.GmailPW)
        s.sendmail(self.msg['From'], [self.msg['To']], self.msg.as_string())
        s.close()

if __name__ == '__main__':
    gmail = Gmail("zeuth717@gmail.com", "************")
    gmail.createMessage("tkhr.karasawa@gmail.com", "title", "body")
    gmail.send()

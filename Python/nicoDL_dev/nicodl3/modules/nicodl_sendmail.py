# -*- coding: utf-8 -*-

import datetime
import smtplib
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import formatdate

class nicodl_sendmail():
    def __init__(self, gmailID, gmailPW, to_addr, cdir=None):
        self.from_addr = gmailID
        self.gmailPW = gmailPW
        self.to_addr = to_addr
        self.date = datetime.datetime.today()

    def create_message(self, from_addr, to_addr, subject, body, encoding):
        # 'text/plain; charset="encoding"'というMIME文書作成
        msg = MIMEText(body, 'plain', encoding)
        msg['Subject'] = Header(subject, encoding)
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Date'] = formatdate()
        return msg

    def send_via_gmail(self, from_addr, to_addr, msg):
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(self.from_addr, self.gmailPW)
        s.sendmail(from_addr, [to_addr], msg.as_string())
        s.close()

    def main(self, msg, preliminary=u""):
        """preliminary: 変換出来なかった時用の文字列"""
        try:
            try:
                msg = self.create_message(self.from_addr, self.to_addr, 'DL compleate.', msg, 'ISO-2022-JP')
            except BaseException:
                print u"Conversion failed"
                msg = self.create_message(self.from_addr, self.to_addr, 'DL compleate.', preliminary, 'ISO-2022-JP')
            self.send_via_gmail(self.from_addr, self.to_addr, msg)
            print 'Send.'
        except Exception, mess:
            print mess
            return False

if __name__ == '__main__':
    a = nicodl_sendmail('myremote717@gmail.com', 'kusounkobaka', 'tkhr-dan-ai@docomo.ne.jp')
    a.main('test')
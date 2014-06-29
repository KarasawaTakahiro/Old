# -*- coding: utf-8 -*-

import datetime
import logging
import os.path
import smtplib
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import formatdate

class nicodl_sendmail():
    def __init__(self, gmailID, gmailPW, to_addr, cdir):
        """
        nicodl_sendmail(from_adress, to_adress, sessage)
        """
        self.from_addr = gmailID #'myremote717@gmail.com'
        self.gmailPW = gmailPW
        self.to_addr = to_addr #'tkhr-dan-ai@docomo.ne.jp'
        self.date = datetime.datetime.today()
        # logging setting
        logfile = ''.join([str(datetime.date.today()), '.txt'])
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(filename)s:%(lineno)d] %(asctime)s %(levelname)s %(message)s',
                            filename=''.join([cdir, '\log\\', logfile]), # logファイル置き場
                            filemode='a')

    def create_message(self, from_addr, to_addr, subject, body, encoding):
        # 'text/plain; charset="encoding"'というMIME文書を作ります
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

    def main(self, msg, idmsg):
        try:
            try:
                msg = self.create_message(self.from_addr, self.to_addr, 'DL compleate.', msg, 'ISO-2022-JP')
            except Exception, mass:
                msg = self.create_message(self.from_addr, self.to_addr, 'DL compleate.', idmsg, 'ISO-2022-JP')
            self.send_via_gmail(self.from_addr, self.to_addr, msg)
            print 'Send.'
            logging.info('Send.')
        except Exception, mess:
            print mess
            logging.error(mess)
            return False

if __name__ == '__main__':
    pass
"""
    from_addr = 'gmail@gmail.com'
    to_addr = 'toadd@gmail.com'
    sendmail = nicodl_sendmail()
    sendmail.main('test',)
"""
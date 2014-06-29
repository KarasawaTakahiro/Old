# coding: utf-8

class CliantInfoFormat():
    def __init__(self, gmail_id=False, gmail_pw=False, nico_id=False, nico_pw=False, toaddr=False, savedir='.'):
        self.gmail_id = gmail_id
        self.gmail_pw = gmail_pw
        self.nico_id = nico_id
        self.nico_pw = nico_pw
        self.toaddr = toaddr
        self.savedir = savedir
        """
        print 'Gmail ID', self.gmail_id
        print 'Gmail PW', u'*'*len(self.gmail_pw)
        print 'Nicovideo ID', self.nico_id
        print 'NIcovideo PW', u'*'*len(self.nico_pw)
        print 'toAddr', self.toaddr
        print 'Savedir', self.savedir
        """

    
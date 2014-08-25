#!/usr/bin/env python
# coding: utf-8

class NicoLoad_table():
    def __init__(self, nicoid=u"", nicopw=u"", gmailid=u"", gmailpw=u"", savedir=u""):
        self.nicoid = nicoid
        self.nicopw = nicopw
        self.gmailid = gmailid
        self.gmailpw = gmailpw
        self.savedir = savedir

    def setNicoid(self, nicoid): self.nicoid = nicoid
    def setNicopw(self, nicopw): self.nicopw = nicopw
    def setGmailid(self, gmailid): self.gmailid = gmailid
    def setGmailpw(self, gmailpw): self.gmailpw = gmailpw
    def setSavedir(self, savedir): self.savedir = savedir
    def getNicoid(self): return str(self.nicoid)
    def getNicopw(self): return str(self.nicopw)
    def getGmailid(self): return str(self.gmailid)
    def getGmailpw(self): return str(self.gmailpw)
    def getSavedir(self): return str(self.savedir)

    def watch(self):
        print type(self.nicoid)
        print self.nicoid


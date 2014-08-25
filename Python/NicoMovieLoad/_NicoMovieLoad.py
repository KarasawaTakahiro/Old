#!/usr/bin/python
# coding: utf-8

import re
from modules.nicoLoad_base import nicoLoad_Base as nicoLoadBase
from modules.nicoLoad_base import Log
from modules.nicoLoad_base import ExcutionStatus
from modules.nicoLoad_load import NicoLoad_Load as nicoLoadLoad
from modules.nicoLoad_database import Database

class NicoMovieLoad(nicoLoadBase):
    def __init__(self):
        nicoLoadBase.__init__(self)
        self.log = Log()
        self.status = ExcutionStatus()
        #self.db = Database()
        self.load = nicoLoadLoad(self.log, self.status, )#self.db)

        self.chPromptStr(u"Welcomeback ;-)")

        self.bind("exit", self.exitMainLoop)
        self.bind("load", self.load.nicoLoad_Load)
        self.bind("rss", self.load.rss)
        self.bind("nico", self.load.regNicoInfo)
        self.bind("gmail", self.load.regGmailInfo)
        self.bind("savedir", self.load.regSavedir)
        self.bind("help", self.help)

    def help(self, *args):
        """help"""
        for i in self.commandDict.keys():
            self.log.log(i, indent=False)

    def exitMainLoop(self, *args):
        self.mainLoop = False
        self.log.log(u"Good bye!\n")
        exit(1)

    def MainLoop(self):
        self.mainLoop = True
        while self.mainLoop:
            while True:
                line = self.prompt()
                if line != None and self.mainLoop: break
            parsedLine = self.parseCommand(line)
            self.runCommand(parsedLine)

if __name__ == "__main__":
    nml = NicoMovieLoad()
    nml.MainLoop()

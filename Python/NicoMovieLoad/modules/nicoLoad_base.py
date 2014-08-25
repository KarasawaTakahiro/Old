#! /usr/bin/env python
# coding: utf-8
"""
nicoLoad_Base
Log
"""

import threading
import Queue

class nicoLoad_Base():
    def __init__(self):
        self.promptStr = u""  # vvgÌ¶ñ
        self.commandDict = {}

    def chPromptStr(self, string):
        self.promptStr = "[%s]: " % string

    def prompt(self):
        inputWord = raw_input(self.promptStr)
        if inputWord.strip(" ") == "":
            return None
        return inputWord

    def parseCommand(self, line):
        """
        ¶ñ©çR}hÆøðo
        return (command, {command:arg, -op1:[arg1-1,...],...})
        """
        lines = line.split()
        command = lines[0]
        args = {}
        arg = []
        for i in xrange(len(lines)):
            if lines[i][0] == '-':
                if len(arg) > 0:
                    args.update({arg[0]:arg[1:]})
                arg = []
                arg.append(lines[i])
            else:
                arg.append(lines[i])
        else:
            args.update({arg[0]:arg[1:]})
        return (command, args)

    def bind(self, command, function):
        """
        R}hÆÖðÖAt¯é
        """
        self.commandDict.update({command:function})
        return True

    def runCommand(self, parsedCommand):
        if not self.commandDict.has_key(parsedCommand[0]):
            # R}hªo^³êÄ¢È©Á½ç
            print '"%s" R}hª©Â©èÜ¹ñB' % parsedCommand[0]
            return False
        
        command = parsedCommand[0]
        th = threading.Thread(target=self.commandDict[command], args=parsedCommand)
        th.setDaemon = True
        th.start()

class Log():
    def __init__(self):
        """
        outputFunction: outputFunction("text") => output: text
        """
        self._texts = Queue.Queue()
        self.__flag = False

        th = threading.Thread(target=self.__print)
        th.daemon = True
        th.start()

    def log(self, *texts, **indent):
        """
        texts: shown strings
        indent: log(indent=True/False) If indent is True, show indent.
        """
        # indent
        if indent.has_key("indent") == False:
            indent = True
        else:
            if type(indent["indent"]) != bool: raise BaseException, u"type(indent) == bool"
            indent = indent["indent"]
        #print "put:", texts
        #self._texts.put_nowait((indent, texts))
        self._texts.put((indent, texts))
        #if self.__flag == False:
        #    th = threading.Thread(target=self.__print)
        #    th.daemon = True
        #    th.start()
        #    self.__flag = True

    def __print(self):
        while True:
           #prints = self._texts.get_nowait()
           prints = self._texts.get()
           for i in xrange(len(prints[1])):
                   self.output(prints[1][i])
           if prints[0]:
               self.output("\n")
           self._texts.task_done()
    """
    def __print(self):
        while True:
            try:
                #prints = self._texts.get_nowait()
                prints = self._texts.get()
                for i in xrange(len(prints[1])):
                        self.output(prints[1][i])
                if prints[0]:
                    self.output("\n")
                self._texts.task_done()
            except:# Queue.Empty:
                pass
    """

    def output(self, text):
        """
        !overwrite!
        it is output function.
        args:
         text: printed strings
        must not indent
        """
        print text,

class ExcutionStatus():
    """
    ÀsÌóÔðÛ·éNX
    """
    def __init__(self):
        self.loadingMovieid = None
        self.loadingMovie = False

    def chLoadingMovie(self, status=None):
        """[h©Ç¤©"""
        if status == None:
            self.loadingMovie = not self.loadingMovie
        else:
            self.loadingMovie = status
    def getLoadingMovie(self):
        """[hµÄ¢é®æðæ¾"""
        return self.loadingMovie

    def setLoadingMovieid(self, movieid):
        """[hÌ®æIDðwè"""
        if not self.getLoadingMovie(): self.chLoadingMovie()
        self.loadingMovieid = movieid
    def getLoadingMovieid(self):
        return self.loadingMovieid
    def initLoadingMovieid(self):
        self.loadingMovieid = None

if __name__ == "__main__":
    import time
    l = nicoLoad_log()
    l.log("jnfoew")
    time.sleep(5)

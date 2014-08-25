#!/usr/bin/python
# coding: utf-8

from nicoLoad_base import Log
from nicoLoad_exceptions import *

class nicoLoad_queue():
    def __init__(self):
        self.__queue = []
        self._got = None
        self.insertNum = 0

    def getQueueList(self):
        return self.__queue

    def add(self, item):
        self.__queue.append(item)
        #print self.__queue

    def addFront(self, item):
        self.__queue.insert(0, item)
        if self.insertNum > 0: self.insertNum += 1
        #print self.__queue

    def addNext(self, item):
        self.__queue.insert(self.insertNum, item)
        self.insertNum += 1
        #print self.__queue

    def get(self):
        if self._got == None:
            if len(self.__queue) == 0:
                self._got = None
                raise QueueEmptyError()
            self._got = self.__queue[0]
            self.__queue.remove(self._got)
            if self.insertNum > 0: self.insertNum -= 1
            else: self.insertNum = 0
            return self._got
        else:
            raise QueueNotOverYetError()

    def done(self):
        self._got = None

    def size(self):
        return len(self.__queue)

    def empty(self):
        if len(self.__queue) == 0:
            return True
        else:
            return False

if __name__ == "__main__":
    import threading
    import time
    log = Log()
    q = nicoLoad_queue()
    def tadd(item):
        t = threading.Thread(target=q.add, kwargs={"item":item})
        t.daemon = True
        #time.sleep(2)
        t.start()
    tadd("sm1")
    q.addFront("sm2")
    tadd("sm3")
    log.log("get:", q.get())
    tadd("sm4")
    #time.sleep(5)
    q.done()
    log.log("get:", q.get())
    #time.sleep(5)
    q.done()
    q.addNext("sm5")
    q.addNext("sm6")
    log.log("get:", q.get())
    q.addFront("sm7")
    q.addNext("sm8")
    while True:
        g = q.get()
        if not g: break
        else: log.log("get:", g)
        q.done()
    time.sleep(2)


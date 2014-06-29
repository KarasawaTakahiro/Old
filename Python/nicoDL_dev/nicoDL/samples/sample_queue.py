#coding: utf-8

import threading
import Queue

class Test(threading.Thread):
    def __init__(self):
        # threading
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.getnumber = Queue.Queue()

    def run(self):
        for i in range(100):
            print i
            if i == 80:
                self.getnumber.put(i)
            if i > 88:
                return
        print "Fin"


test = Test()
test.start()
#test.join()

number = test.getnumber.get()

print u"Last number is", number







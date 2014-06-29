#! /usr/bin/env python
# coding: utf-8

# progressbar.py

import sys
class progressBar:
    def __init__(self, whole, length=30, ch="#", nch=" "):
        self.whole = whole
        self.length = length
        self.ch = ch
        self.nch = nch
    def update(self, current):
        ret = ""
        end = current / self.whole # 何パーセント終わったか
        x = int(end * self.length)  # プログレスバーの長さのうちどれだけ終わったか
        ret += "["
        for _ in range(0, x+1):
            ret += self.ch
        for _ in range(x+1, self.length):
            ret += self.nch
        ret += "] %d%%\r" % int(end * 100.0)
        return ret
    def flush(self, current):
        print self.update(current),

#######################

def test():
    import time
    bar = progressBar(100)
    for i in range(0, 100):
        bar.flush(float(i))
        time.sleep(0.05)
    print # newline

def toy():
    import time
    foo = progressBar(100)
    def f(message, interval):
        for i in range(0, 100):
            print message, foo.update( float(i) ),
            sys.stdout.flush()
            time.sleep(interval)
        print # newline
    f("initialize component : \n", 0.05)
    f("extract program      : \n", 0.02)
    f("execute program      : \n", 0.1)
    f("finalize component   : \n", 0.001)


if __name__ == '__main__':
    toy()
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# shutdown 1.0

import time, os

# シャットダウン
def shutdown(limhour, limminute):
    while 1:
        nowdate = time.ctime()
        nowdate = nowdate.split(" ")
        nowtime = nowdate[-2].split(":")
        del nowtime[-1]

        def get_nowhour():
            nowhour = int(nowtime[0])
            return nowhour

        def get_nowminute():
            nowminute = int(nowtime[1])
            return nowminute

        nowhour = get_nowhour()
        nowminute = get_nowminute()
        if limhour == nowhour and limminute == nowminute:
            print u"now   ", nowhour, u":", nowminute
            print u"limite", limhour, u":", limminute
            os.system("shutdown -s -f -t 60")
            break
        else:
            print u"now   ", nowhour, u":", nowminute
            print u"limite", limhour, u":", limminute
            time.sleep(60)
            continue

if __name__ == "__main__":
    f = open("time.txt").readline().split(":")
    hour = int(f[0])
    minute = int(f[1])
    shutdown(hour, minute)
    print u"シャットダウン"

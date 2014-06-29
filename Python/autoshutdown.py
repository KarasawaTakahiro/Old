#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time,os

# 現時刻
def get_nowtime():    # 現時・分を取得
    nowdate = time.ctime()
    nowdate = nowdate.split(" ")
    nowtime = nowdate[-2].split(":")
    del nowtime[-1]
    return nowtime

def get_nowsecond():   # 現時刻（分）を取得
    nowdate = time.ctime()
    nowdate = nowdate.split(" ")
    nowtime = nowdate[-2].split(":")
    nowsecond = nowtime[-1]
    return nowsecond

def get_nowhour():    # 現時刻（時）を取得
    nowhour = int(get_nowtime()[0])
    return nowhour

def get_nowminute():    # 現時刻（秒）を取得
    nowminute = int(get_nowtime()[1])
    return nowminute

def get_limhour():    # 予定時刻（時）を取得
    limhour = input(u"24-hour time limit input (hours)\nhours==>")
    while True:
        try:
            limhour = int(limhour)
            return limhour
            break
        except:
            print u"数字を入力"
            limhour = input(u"24-hour time limit input (hours)\nhours==>")

def get_limminute():    # 予定時刻（分）を取得
    limminute = input(u"24-hour time limit input (min)\nminute==>")
    while True:
        try:
            limminute = int(limminute)
            return limminute
            break
        except:
            print u"数字を入力"
            input(u"24-hour time limit input (min)\nminute==>")


# shutdown
def shutdown(limhour, limminute):
    print u"---------------------------------"
    print limhour , u":", limminute,  u" にシャットダウンします。"

    waittime = 60 - int(get_nowsecond())    # 時間調整
    time.sleep(waittime)

    while 1:
        nowhour = get_nowhour()
        nowminute = get_nowminute()
        if limhour == nowhour and limminute == nowminute:
            print u"---------------------------------"
            print u"時間になりました。\n20秒後にシャットダウンされます。"
            print u"limite", limhour, u":", limminute
            os.system("shutdown -s -f -t 20")
            break
        else:
            print u"---------------------------------"
            print u"now   ", nowhour, u":", nowminute
            print u"limite", limhour, u":", limminute
            time.sleep(60)
            continue

        time.seep(5)

# main
if __name__ == "__main__":
    hour = get_limhour()
    minute = get_limminute()
    shutdown(hour, minute)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time,os

class Timer():
    u"""タイマー"""
    def __init__(self):
        self.nowdate = time.ctime().split()

    def main(self):
        # 現時・分を取得
        self.nowtime = self.nowdate[-2].split(":")
        # 現時刻（秒）を取得
        self.nowminute = int(self.nowdate[-2].split(':')[-1])
        # 予定時刻の入力
        print u'実行時間を入力してください\n　Ex) pm.11:01 -> 23 01'
        self.c = 0
        self.w = False
        while True:
            try:
                if self.c >= 2:
                    print u'中止しますか？'
                    self.cancel = raw_input('--y/n? :')
                    if self.cancel == 'y':
                        return True
                    else:
                        self.c = 0
                elif not 0<= int(self.limtime[0]) <= 24:
                    print u'24時間で入力してください。'
                    self.c += 1
                    raise InputError
                elif not 0<= int(self.limtime[1]) <= 59:
                    print u'0-59分の間で入力してください。'
                    self.c += 1
                    raise InputError
                print u'%i:%i に設定します。' % (int(self.limtime[0]), int(self.limtime[1]))
                self.ans = raw_input('--y/n? : ')
                if self.ans == 'y':
                    break
                if self.ans == 'n':
                    self.c += 1
                    raise InputError
                else:
                    pass
            except:
                if self.w:
                    print u'実行時間を入力してください。'
                self.limtime = raw_input('>>>').split()
                self.w = True
            # self.limtime が決まる

                
    """


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

            print u"シャットダウン"
            time.seep(5)"""

# main
if __name__ == "__main__":
    timer = Timer()
    timer.main()
    

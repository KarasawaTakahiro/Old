# -*- coding: utf-8 -*-

import win32clipboard as cb
import time

def get_board():
    
    time.sleep(0.5)

    cb.OpenClipboard()
    text = cb.GetClipboardData(1)
    cb.CloseClipboard()
    return text

# main code
if __name__ == '__main__':

# 値
    c = 0
    text = get_board()
    otext = None

# 分岐
    while True:
        text = get_board()
        
        if text == "quit":    # 終了
            break
        elif text != otext:    # 表示
            print "----------------------------------------------------"
            print text, "\n"
            
            f = open("log.txt", "a")
            f.write(text+"\n""\n"+"\\\\"+"\n""\n")    # ファイルに書く
            f.close
            c = 0
        elif text == otext:    # かぶった時
            c += 1
            print "==", c
            
            continue
        else:
            print 'else'

        otext = text

# end
    f.close()

    for t in renge(1,3):    # カウントダウン
        print t
        time.sleep(1)

    print "fin"

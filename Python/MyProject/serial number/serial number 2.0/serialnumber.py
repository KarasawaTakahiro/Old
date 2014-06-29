# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os, os.path, shutil, time

#値の設定 
directory = os.getcwd()
before = directory + "\\before"
after = directory + "\\after"
origine = directory + "\\origine"
f = open("filename.txt","r")
fno = 1
sno = 1
items = []

# ファイル名読み込み
f = open("filename.txt","r")
f = f.read()
f = f.split(".")
name = f[0]
fno = f[1]
sno = f[2]

# 変換
for items in os.walk("before"):
    items = items[-1]
    
    for item in items:
        shutil.copy2(before + "\\" + item, origine)    # コピー
        print "-----------------------------------------"
        print "copy   => ", item

        itemname = item.split(".")    # 拡張子取得
        itemend = itemname[-1]        #

        cname = name + " " + fno + "-" + str(sno) + "." + itemend    # 結合

        os.rename(before + "\\" + item, after + "\\" + cname)    # 変換
        print "rename => ", cname

        sno =int(sno)
        sno += 1

print "complete"
time.sleep(5)

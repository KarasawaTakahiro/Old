# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import shutil

#値の設定
directory = os.getcwd()
before = directory + "\\before"
after = directory + "\\after"
origine = directory + "\\origine"
items = []
dotou = "ELF"



# 変換
for items in os.walk("before"):
    items = items[-1]
    print items

for item in items:
    shutil.copy2(before + "\\" + item, origine)    # コピー
    e = dotou + str("-") + str(item)

    b =  "%(before)s\\%(citem)s" % \
          {"before":before,"citem":item}
    d = "\\"
    a = after + "\\" +e
    print b
    os.rename(b,a)
    print "    ||"
    print "    \/"
    print a

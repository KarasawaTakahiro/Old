# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import time

#値の設定
directory = os.getcwd()
before = "".join((directory, "\\before"))
after = "".join((directory, "\\after"))
origine = "".join((directory, "\\origine"))
items = []
boutou = "Umineko"

# フォルダ作成
for a in (before, after, origine):
    p = os.path.exists(a)
    if p == False:
        os.mkdir(a)
del a, p

# 一覧
for items in os.walk("before"):
    items = items[-1]
for item in items:
    print item
    
print

for item in items:
    ofile = os.path.join(before, item)
    root, ext = os.path.splitext(ofile)
    shutil.copy2(ofile, origine)    # バックアップ
    oname = item.split(" ")    # ファイル名分解
    ep = oname[1].lstrip('Ep').rjust(2, '0')
    kai = oname[2].split('-')
    kai1 = kai[0]
    kai2 = kai[1].rstrip(ext)
    name = "".join((boutou, ' ', 'Ep', ep, ' ', kai1, '-', kai2, ext))
    filename = os.path.join(after, name) # ファイル名決定
    print name
    print 
    try:
        os.rename(ofile, filename)
    except:
        pass

    print u'次！'
    for a in range(30):
        print '-',
    print '\n'
    
print 'End'
time.sleep(5)

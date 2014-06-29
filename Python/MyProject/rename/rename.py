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
boutou = u'焼きたて!!ジャぱん'#raw_input(u'タイトル>> ')

# フォルダ作成
for a in (before, after, origine):
    p = os.path.exists(a)
    if p == False:
        os.mkdir(a)
del a, p

# 一覧
print u'一覧'
for items in os.walk("before"):
    items = items[-1]
for item in items:
    print item

print

back = raw_input(u'バックアップを取りますか？\n Y/N >>> ') # バックアップ確認
if back == 'Y' or back == 'y':
    back = True
elif back == 'N' or back == 'n':
    back = False
else:
    print u'else'
    back = True

for item in items:
    print item
    ofile = os.path.join(before, item)
    ext = os.path.splitext(ofile)[1]
    if back == True:
        shutil.copy2(ofile, origine)    # バックアップ
    oname = item.split(" ")    # ファイル名分解
    ep = oname[2].lstrip('ep').rjust(2, '0') # ep は適宜変更
    kai = oname[3]         # ex)1/3
    kai1 = list((kai))[0]  #    1
    kai2 = list((kai))[2]  #    3
    name = u"".join((boutou, ' ', 'Ep', ep, '-', kai1, '_', kai2, ext))
    filename = os.path.join(after, name) # ファイル名決定
    print name
    print
    try:
        os.rename(ofile, filename)
        print u'成功！'
    except:
        print u'失敗。。。'
        pass

    print u'次！'
    for a in range(30):
        print '-',
    print '\n'

print 'End'
time.sleep(5)

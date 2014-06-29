#coding: utf-8

import pickle
import os

lib=r"C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\Dropbox\nicoDL_dev\nicoDL\data\library_ALL.ndl"


ed = []

f = open(lib)
items = pickle.load(f)
flag = True
for item in items:  # item == dict
    lis = item.items()
    for (key, factor) in lis:  # print用ループ
        print key, ':',factor
    if flag == True:
        print u'削除しますか？'
        i = raw_input('y/n/skip >>> ')
        if i == 'y': pass
        elif i == 'skip':
            ed.append(item)
            flag = False
        else:
            ed.append(item)
    else:
        ed.append(item)
    print

print u'保存しますか？'
i = raw_input('y/n >>> ')
if i == 'y':
    f = open(lib, "w")
    pickle.dump(ed, f)
    f.close()
else:
    import datetime
    (front, end) = os.path.splitext(lib)
    lib = ''.join([front, str(datetime.datetime.now()).replace(":", "-"), end])
    f = open(os.path.join(lib), "w")
    pickle.dump(ed, f)
    f.close()

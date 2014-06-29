# coding: utf-8

import os
import sys
enc = sys.getfilesystemencoding()
try:
    ff = open('os_walk.txt','w')
    for root, dirs, files in os.walk(r'C:\Users\KarasawaTakahiro\Videos\DARK SOULS', topdown=False):
        ff.write(u'Root:\n'.encode('utf-8'))
        ff.write(root.decode(enc).encode('utf-8'))
        ff.write(u'\n'.encode('utf-8'))
        ff.write(u'Dirs:\n')
        for item in dirs:
            ff.write(item.decode(enc).encode('utf-8'))
            ff.write(u'\n'.encode('utf-8'))
        ff.write(u'Files:\n'.encode('utf-8'))
        for item in files:
            ff.write(item.decode(enc).encode('utf-8'))
            ff.write(u'\n'.encode('utf-8'))
        ff.write(u'\n'.encode('utf-8'))
finally:  ff.close()

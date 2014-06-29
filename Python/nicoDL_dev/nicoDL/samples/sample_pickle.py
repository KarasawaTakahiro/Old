#!/usr/bin/env python
#-*- coding: utf-8 -*-

import pickle
def a():
    '''pickleの使い方'''

    '適当なオブジェクトを用意する'
    o = [1, 2, 3, (1, 2, 3), set([(1, 2), 1, 2, 3, 4])]

    print o #[1, 2, 3, (1, 2, 3), set([(1, 2), 1, 2, 3, 4])]


    """書き込みモードで開く"""
    opened = open('test.dump','w')

    '''pickle化'''
    pickle.dump(o,opened)
    '''同ディレクトリにtest.dumpとして保存されている'''

    opened.close()

    '''dumpファイルを開く'''
    opened2 = open('test.dump')

    o2 = pickle.load(opened2)

    print o2 #[1, 2, 3, (1, 2, 3), set([(1, 2), 1, 2, 3, 4])]
    '''ちゃんとオブジェクトとして再現できる'''
    print o2[3][2] #3

    o2.append({'hoge':'foo'})

    print o2 #[1, 2, 3, (1, 2, 3), set([(1, 2), 1, 2, 3, 4]), {'hoge': 'foo'}]
    opened2.close()

    opened3 = open('test.dump','w')

    '再度保存するときはdump'
    pickle.dump(o2,opened3)

a()
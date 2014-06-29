#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import sys
import time



def set_directory():
    cdir = ur'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\Program\MyProject\rename'
    directory1 = ur"C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\Temporary Files"
    # バックアップ用フォルダ
    backdir = os.path.join(cdir, 'back up')
    # 変更前フォルダ
    indir = os.path.join(cdir, 'before')
    # 変更後フォルダ
    outdir = os.path.join(cdir, 'after')
    question = u'''Enter. %s\n1. %s''' % (directory1, outdir)
    print question
    doutdir = raw_input(u'nunber>>> ')
    if doutdir == u'':
        outdir = directory1
    elif doutdir == u'1':
        pass
    else:
        pass
    del question
    # フォルダ作成
    for a in (indir, outdir, backdir):
        p = os.path.exists(a)
        #print p, a
        if p == False:
            os.mkdir(a)
            print u'maked %s' % a
            print
    del a, p

    return (indir, outdir, backdir, cdir)

def question():
    q = raw_input(u'Yes/No >>> ').lower()
    if q == u'yes' or q == u'y':
        q = True
    elif q == u'no' or q == u'n':
        q = False
    else:
        q = None
    return q

def mkdic(path, name, outdir=None):
    d = {}
    d['path'] = path
    d['name'] = name
    d['fpath'] = os.path.join(path, name)
    d['outdir'] = outdir
    return d

def orderdic(character, number):
    d = {}
    d[character] = number
    return d

def namefac(fnames):
    u"""ファイル名のリストを渡す"""
    #myprint(fnames)
    itemlen = len(fnames)
    counter = []
    replace = {} # 順番辞書
    words = [] # 辞書用
    indexes = [] # 辞書用
    while True:
        print u'対応する数字で順番を入力'
        for word in fnames:
            counter.append(len(word))
            words.append(word)
            print word, # 必要
        print # 重要空白行
        for index in range(1,itemlen+1):
            for space in counter:
                #print '%i-%i' % (index,space)
                s = u'_'*(space-1)
                print '%i%s' % (index, s), # 必要
                indexes.append(index)
                counter.remove(counter[0])
                break
        print # 必要空白行
        for a in zip(indexes, words): # 辞書作成
            replace[a[0]] = a[1]
        indexprolist = []
        for a in xrange(1, index+1):
            while True:
                print a, u'番目',
                indexpro = raw_input(u'>>> ')
                if indexes.count(int(indexpro)) == 0:
                    print u'見つかりません...'
                    continue
                break
            print u'=>', indexpro
            indexprolist.append(int(indexpro))
        print
        while True:
            for a in indexprolist: # 名前表示
                print replace[a],
            print # 必要空白行
            print u'でいいですか？' # 確認
            q = question()
            if q == None:
                continue
            elif q == False:
                print u'-> No!'
            break
        if q == True:
            break

    #
    # ここまで####

    indexes = indexprolist # よければ上書き
    #print indexes
    #print words
    replace = {}
    for a in zip(indexes, words): # 上書きで辞書作成
        #print a
        replace[a[0]] = a[1]

    filename = u''
    for a in xrange(1, index+1):
        filename =  u' '.join([filename, replace[a]])
    c = 0 # 頭のスペース除去
    s = u''
    for i in filename:
        if i == u' ' and c == 0:
            c +=1
        else:
            s = u''.join([s, i])
    filename = s
    print u'-> %s\nを使います.' % filename
    print # 空白
    return filename



def main():
    fileenc = sys.getfilesystemencoding()

    print u'--開始---------------------------------------------------------'
    print
    print u'保存先のフォルダを選んでください.'
    dirs = set_directory()
    indir = dirs[0]
    outdir = dirs[1]
    backupdir = dirs[2]
    cdir = dirs[3]
    files =[]
    # ファイルの決定
    c = 1
    for item in sys.argv: # ファイルが引数で与えられた場合
        if c == 1:
            c += 1
            continue
        fpath = os.path.dirname(item)
        fname = os.path.basename(item)
        itemdic = mkdic(fpath, fname, outdir)
        files.append(itemdic)
    for items in os.walk(indir): # indir 参照
        if not items[2] == []:
            for i in items[2]:
                itemdic = mkdic(items[0], i, outdir)
                files.append(itemdic)
    if len(files) == 0: # ファイルが無かったら終了
        print # 空白
        print u'変更元ファイルが見つかりません...'
        print u'Enter で終了.'
        raw_input('')
        return
    # 一覧
    print u'以下のファイル名を変更'
    for item in files:
        print u'-> ', item['name']
    print # 空白
    # バックアップ確認
    print u'バックアップを取りますか？'
    while True:
        backup_q = question()
        if backup_q == None:
            print u'バックアップを取りますか？'
            continue
        break
    if backup_q == True:
        print u'-> Yes!'
    else:
        print u'-> No!'
    print # 空白
    # 変更処理
    oldnamedir = os.path.join(cdir, 'oldname.txt')
    oldnamedirexeist = os.path.lexists(oldnamedir)
    if oldnamedirexeist == True: # 前回の名前の保存ファイルを開く
        old = open(oldnamedir, 'r')
        oldname = old.readline().decode(fileenc)
        old.close()
    namesave = False # 保存用
    while True: # 前回の名前を使うか確認
        if oldnamedirexeist == True: #
            print u'前回の名前を使いますか？\n %s' % oldname
            name_q = question()
            if name_q == True:
                name = oldname
            if name_q == None:
                continue
        if (oldnamedirexeist == False
           or oldnamedirexeist == True and name_q == False): # 前回の名前を使わなければ入力、上書き
            print u'名前を入力'
            proname = raw_input(u'>>> ')
            while True:
                print u'%s\nでいいですか？\n' % proname
                name_q_q = question()
                if name_q_q == None:
                    print u'%s\nでいいですか？\n' % proname
                    continue
                elif name_q_q == False:
                    print u'名前を入力'
                    proname = raw_input(u'>>> ')
                    continue
                elif name_q_q == True:
                    name = proname
                    namesave = True
                break
        break
    print u'-> %s\nを使います.' % name
    print # 空白
    if namesave == True:
        savefile = open('oldname.txt', 'w')
        savefile.write(name)
        savefile.close()
    # 名前以外の決定とリネーム
    c = 1
    for item in files:
        #print item
        if not c == 1:
            print u'次！'
            print # 空白
        for a in xrange(40):
            print u'-',
        print # 空白
        print # 空白
        print u'処理開始.'
        print u' %s' % item['name']
        print # 空白
u"""
namefac の引数決定
使う単語のリストを渡す

        item['name']

        filename = namefac() # ファイル名決定
"""

        if backup_q == True: # バックアップ
            backupfile = os.path.join(backupdir, item['name'])
            print u'バックアップを保存中...'
            print u' %s' % item['name']
            shutil.copy2(item['fpath'], backupfile)
            print u'バックアップ完了！'
            print u'-> ', backupfile
            print # 空白
        print u'リネーム中...'
        print ''.join([u'%s \n   ↓↓↓\n', filename]) % item['name']# 名前の表示
        print # 空白
        renameoutdir = os.path.join(item['outdir'],filename)
        os.rename(item['fpath'], renameoutdir)
        print u'リネーム完了！'
        print u'->', renameoutdir
        print # 空白

    print u'Enter で終了.'
    raw_input('')

if __name__ == '__main__':
    main()
    """
    try:
        main()
        print
        raw_input('waiting... Push Enter')
    except Exception, a:
        print
        print
        print 'Error raise.'
        print a
        raw_input('waiting... Push Enter')
    """


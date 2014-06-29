#!/usr/bin/env python
# -*- coding:utf-8 -*-


import os.path

def question():
    q = raw_input(u'Yes/No >>> ').lower()
    if q == u'yes' or q == u'y':
        q = True
    elif q == u'no' or q == u'n':
        q = False
    else:
        q = None
    return q

def orderdic(character, number):
    d = {}
    d[character] = number
    return d

def main(fnames):
    """ファイル名のリストを渡す"""
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


if __name__ == '__main__':
    filename = u'Yakitate!! Japan ep99 9_9'
    filenames = filename.split(u' ')
    main(filenames)

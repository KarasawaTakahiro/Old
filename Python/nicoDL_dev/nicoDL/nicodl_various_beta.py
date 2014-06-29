#!/usr/bin/env python
#-*- coding: utf-8 -*-

import libraryformat
import nicovideo
import os
import pickle

class nicoDL_Various():
    def __init__(self, libraryfilepath=False):
        u"""
        libraryfilepath : ライブラリファイルのある場所
        make_myformatを呼ぶ限りはlibraryfilepath引数はいらない
        """
        if libraryfilepath != False:
            self.libraryfile = os.path.join(libraryfilepath, 'Library.ndl')

    def make_myformat(self, form=False,
                            movie_id=False, movie_name=False,
                            movie_path=False, movie_size=False,
                            mylist_id=False, mylist_name=False,
                            mylist_description=False, rss=True,
                            state=False, priority=-1,
                            option=False, downloaded=[]
                            ):
        u"""
        return myformat

        フォーマット
        form               : MOVIE/MYLIST 差別用
        movie_id           : unicode
        movie_name         : unicode
        movie_path         : unicode 動画ファイルパス
        movie_size         : unicode 動画サイズ
        mylist_id          : unicode
        mylist_name        : unicode
        mylist_description : unicode マイリス説明
        rss                : bool RSSするか
        priority           : int
        state              : bool DLしたか
        option             : unicode
        thumbnail          : unicode サムネ保存ディレクトリ

        movie_id か mylist_id のどちらかは必須
        form == "MOVIE" or "MYLIST" 無くてもいい
        """
        if not form: raise ValueError, u"formが入力されていません."

        if movie_id != False or form == "MOVIE":
            form = "MOVIE"
            rss = False
        elif mylist_id != False or form=="MYLIST":
            form = "MYLIST"
            rss = True
        else: raise ValueError, u"IDが入力されていません."

        return libraryformat.LibraryFormat(movie_id=movie_id, movie_name=movie_name,
                                           movie_path=movie_path, movie_size=movie_size,
                                           mylist_id=mylist_id, mylist_name=mylist_name,
                                           mylist_description=mylist_description,
                                           rss=rss, downloaded=downloaded,
                                           state=state, priority=priority,
                                           option=option, form=form)

    def open(self):
        u"""
        ライブラリファイルを開く

        return libdata
        """
        #print self.libraryfile
        # ライブラリファイルがないとき
        if not os.path.exists(self.libraryfile):
            print u'ライブラリファイルを新規作成します。'
            # LibraryFormat作成
            lib = {'MOVIE' :{},
                   'MYLIST':{} }
            for item in lib:
                #print item
                for a in xrange(0,10):
                    lib[item][a] = []
            #print u'作成\n ',lib

            self.save(lib)  # いったん保存
            return lib

        ff = open(self.libraryfile, 'r')
        try:     lib = pickle.load(ff)
        finally: ff.close()
        return lib

    def save(self, lib_obj):
        u"""
        ライブラリファイルを上書き保存して閉じる

        return
        """
        try:
            ff = open(self.libraryfile, 'w')
            pickle.dump(lib_obj, ff)
        finally:
            ff.close()

    def write_library(self, myformat_obj):
        """
        myformat_obj: myformat_obj

        library.ndl を開いてアイテムを追記していく
        """
        # ここで割り振り
        #print u'割り振り'
        u"""
        myformat_obj: 振り分け待ち
        lib     : libraryfile
        """
        # 指定
        #print 'form:',myformat_obj.form
        if myformat_obj.form == 'MOVIE':
            s1 = 'MOVIE'
            s2 = myformat_obj.below
        elif myformat_obj.form == 'MYLIST':
            s1 = 'MYLIST'
            s2 = myformat_obj.below
        else: raise ValueError
        #print 's1:',s1
        #print 's2:',s2

        lib = self.open()  # libfile開く

        # 重複チェック
        #print u'重複チェック'
        flag = True  # 追加するか
        for item in lib[s1][s2]:
            if s1 == 'MOVIE':
                ID = item.movie_id
                obj_ID = myformat_obj.movie_id
            elif s1 == 'MYLIST':
                ID = item.mylist_id
                obj_ID = myformat_obj.mylist_id
            # 被ってたらフラグ変更
            if ID == obj_ID:
                #print u'ダブり'
                flag = False
                if form == 'MOVIE':
                    # ダウンロード済みをFalseに
                    item.state = False
                    print u'%sのダウンロード済みをリセット' % item.movie_name
                elif form == 'MYLIST':
                    # ダウンロード済みを空に
                    item.downloaded = []
                    print u'%sのダウンロード済みをリセット' % item.mylist_name
                break

        if flag:
            #print u'追加'
            lib[s1][s2].append(myformat_obj)
        else: pass
            #print u'追加せず'

        self.save(lib)
        #print 'lib:\n', lib

        return True

    def pickup(self, movie_id=False, mylist_id=False, choice=None):
        u"""
        choice->
            form               : MOVIE/MYLIST 差別用

            movie_id           : unicode
            movie_name         : unicode
            movie_path         : unicode 動画ファイルパス
            movie_size         : unicode 動画サイズ
            state              : bool DLしたか
            thumbnail          : unicode サムネ保存ディレクトリ

            mylist_id          : unicode
            mylist_name        : unicode
            mylist_description : unicode マイリス説明
            rss                : bool RSSするか

            priority           : int
            option             : unicode

            None               : myform_obj


        return value
        """
        lib = self.open()

        if movie_id != False:
            form = 'MOVIE'
            below = int(movie_id[-1])
        elif mylist_id != False:
            form = 'MYLIST'
            below = int(mylist_id[-1])
        else: raise ValueError

        #print lib[form]
        #print lib[form][below]

        for item in lib[form][below]:
            # item == myformat_obj #
            if form == 'MOVIE':
                # ヒットしてchoiceが与えられていない
                if (item.movie_id == movie_id) and (choice == None):
                    return item  # myform_objを返す
                # ヒットしてchoiceが与えられている
                elif (item.movie_id == movie_id) and not(choice == None):
                    break
            elif form == 'MYLIST':
                # ヒットしてchoiceが与えられていない
                if item.mylist_id == mylist_id and (choice == None):
                    return item  # myform_objを返す
                # ヒットしてchoiceが与えられている
                elif item.mylist_id == mylist_id and not(choice == None):
                    break
        # ヒットしないでループ終了
        else: raise ValueError, '見つかりませんでした'

        return getattr(item, choice)


    def rewrite_library(self, factor, value, movie_id=False, mylist_id=False):
        u"""
        factor : 書き換える値のkey
        value : 書き換える値
        movie_id, mylist_id : 参照 どちらか必要
        """
        lib = self.open()

        u"""ココから"""

        #if movie_id:
        #elif mylist_id:
        #else: raise ValueError

        c = 0
        #print lib
        for dic in lib:
            if (dic["format"] == "MYLIST") and (dic["mylist_id"] == mylist_id):
                #print dic
                # mylist を先に判定しないとダメ
                if key == "downloaded":
                    dic[key].append(value)
                else:
                    dic[key] = value
            elif (dic["format"] == "MOVIE") and (dic["movie_id"] == movie_id):
                #print dic
                dic[key] = value
            else:
                c += 1
                continue
            #print lib
            # 要素を入れなおす
            del lib[c]
            lib.insert(c, dic)
            del c
            break

        self.save(lib)

    def reflesh_libraryfile(self):
        data = self.open()

        for i in xrange(len(data)):
            try:
                data.remove(False)
            except ValueError:
                break
        data.reverse()

        self.save(data)

    def getmovieIDs(self, down=False):
        u"""
        ライブラリ内の動画IDの一覧
        down : int0-9
        downに引数を与えるとそのレベル内のみの一覧を返す
        return []
        """
        if not(down in range(0,10)) and not(down==False):
            # 引数が想定外
            raise ValueError(u'downは0-9のint')

        lib = self.open()
        movies = []
        if down == False:
            for index in xrange(0,10):
                for item in lib['MOVIE'][index]:
                    movies.append(item.movie_id)
        else:
            for item in lib['MOVIE'][down]:
                movies.append(item.movie_id)

        return movies

    def getmylistIDs(self, down=False):
        u"""
        ライブラリ内のマイリスIDすべての一覧
        down : int0-9
        downに引数を与えるとそのレベル内のみの一覧を返す
        return []
        """
        if not(down in range(0,10)) and not(down==False):
            # 引数が想定外
            raise ValueError(u'downは0-9のint')

        lib = self.open()
        mylists = []
        if down == False:
            for index in xrange(0,10):
                for item in lib['MYLIST'][index]:
                    mylists.append(item.mylist_id)
        else:
            for item in lib['MYLIST'][down]:
                mylists.append(item.mylist_id)

        return mylists

    def rsscheck(self):
        """
        ライブラリ内のマイリストについて
        webのマイリストと比較し未DL動画があればライブラリに追加
        """
        items = self.open()["MYLIST"]
        for index in xrange(0,10):
            for item in items[index]:
                print u"RSS:", item.mylist_id
                downloaded = item.downloaded
                try:
                    niconicovideo = nicovideo.Nicovideo(mylist_id=item.mylist_id)
                except:  # 接続失敗
                    print u"ニコニコ動画に接続失敗..."
                    return False
                movies = niconicovideo.get_mylist_movies()
                #print movies
                for movie in movies:
                    #print '*****************************'
                    try:
                        downloaded.index(movie)
                        continue
                    except ValueError:
                        # movie_id がdownloaded に 無い時
                        """
                        myform_m: すでに登録済みIDリスト
                        movie : 追加したいmovie_id
                        """
                        myform_m = self.getmovieIDs(int(movie[-1]))
                        if movie in myform_m:
                            # 登録済み
                            continue
                        else:
                            # 未登録
                            print u'RSSHit: %s' % movie
                            self.write_library(self.make_myformat(movie_id=movie, mylist_id=item.mylist_id, form='MOVIE'))



if __name__ == "__main__":
    va = nicoDL_Various(libraryfilepath=os.getcwd())

    form = va.make_myformat(mylist_id='28198743', mylist_name=u'ダークソウルRTA',form='MYLIST')
    va.write_library(form)
    va.rsscheck()
    #print va.getmovieIDs()
    #print va.getmylistIDs()

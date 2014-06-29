#!/usr/bin/env python
#-*- coding: utf-8 -*-

import libraryformat
import nicovideoAPI
import os
import pickle

class nicoDL_Various():
    def __init__(self, libraryfilepath=False, libraryfilename='Library.ndl'):
        u"""
        libraryfilepath : ライブラリファイルのある場所
        make_myformatを呼ぶ限りはlibraryfilepath引数はいらない
        """
        if libraryfilepath != False:
            self.libraryfile = os.path.join(libraryfilepath, libraryfilename)

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

        form               : MOVIE/MYLIST 差別用
        below              : int IDの下一桁
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

        movie_id か  mylist_idのどちらかは必須
        form == "MOVIE" or "MYLIST"
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

    def libopen(self):
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

        libfile = open(self.libraryfile, 'r')
        try:     lib = pickle.load(libfile)
        finally: libfile.close()
        return lib

    def save(self, lib_obj):
        u"""
        *ライブラリファイルを上書き保存して閉じる
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

        library.ndlを開いてアイテムを記述していく
        """
        # ここで割り振り
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

        lib = self.libopen()  # libfile開く

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
            # かぶってたらフラク変更
            if ID == obj_ID:
                #print u'ダブり'
                flag = False
                if item.form == 'MOVIE':
                    # ダウンロード済みをFalseに
                    item.state = False
                    print u'%sのダウンロード済みをリセット' % item.movie_name
                elif item.form == 'MYLIST':
                    # ダウンロード済みをリセット
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

    def deldata(self, movie_id_list=[], mylist_id_list=[]):
        """
        *指定したIDをlibファイルから削除する
        *リストで指定
        *削除出来なかったidはリストで返す
        """
        def kyoutuu(myformatparent, item, form):
            """共通部分の簡略化"""
            erroritems = []
            below = int(item[-1])
            myformatlist = myformatparent[form][below]  # こども
            # ほしいmyformatの抽出
            no = 0  # ほしいmyformatのインデックス
            for myformat in myformatlist:
                # breakした時点で,noにインデックスが入ってる
                if form == 'MOVIE':
                    if myformat.movie_id == item:  break
                else:  
                    if myformat.mylist_id == item:
                        break
                no += 1
            try:  # 削除
                del myformatlist[no]
            except IndexError:  # 削除出来なかった
                erroritems.append(item)
            return (myformatlist, below, erroritems)

        myformatparent = self.libopen()  # 全体
        #print myformatparent
        erroritems = []

        # movieの処理
        for item in movie_id_list:
            # item == movie_id
            #print 'movie:', item
            form = 'MOVIE'
            # マイリスから来てる
            #frommylist = self.pickup(movie_id=item, choice='mylist_id')
            myformatlist, below, erroritem = kyoutuu(myformatparent, item, form)
            myformatparent[form][below] = myformatlist  # 入れ直し
            erroritems.extend(erroritem)  # 削除出来なかった分
            """削除したデータにマイリスからのがあったらマイリスのダウンロード済みから除外しないと"""
            #if frommylist:
                
        
        # mylistの処理
        for item in mylist_id_list:
            # item == mylist_id
            #print 'mylist:', item
            form = 'MYLIST'
            myformatlist, below, erroritem = kyoutuu(myformatparent, item, form)
            myformatparent[form][below] = myformatlist  # 入れ直し
            erroritems.extend(erroritem)  # 削除出来なかった分

        #print erroritems
        self.save(myformatparent)
        return erroritems

    def pickup(self, movie_id=False, mylist_id=False, choice=None):
        u"""
        choice->
            form               : MOVIE/MYLIST差別用
            
            movie_id           : unicode
            movie_name         : unicode
            movie_path         : unicode 動画ファイルパス
            movie_size         : unicode 動画ファイルサイズ
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
        lib = self.libopen()

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
        # ヒットせず終了
        else: raise ValueError, u'見つかりませんでした'

        return getattr(item, choice)


    def rewrite_library(self, factor, value, movie_id=False, mylist_id=False, chengedownloaded=1):
        u"""
        factor : 書き換える値のkey
        value :  書き換える値
        movie_id, mylist_id : 参照　どちらか必要
        chengedownloaded: マイリスのDL済みを変更するときの引数
                          *正の値 => 追加
                          *負の値 => 削除
        """
        if not(movie_id == False) and not(mylist_id == False):
            raise ValueError, u'movie_id,mylist_idはどちらかにしてください。'

        if movie_id: 
            form = 'MOVIE'
            below = int(movie_id[-1])
        else: 
            form = 'MYLIST'
            below = int(mylist_id[-1])
        myformatparent = self.libopen()  # 全体
        myformatlist = myformatparent[form][below]  # こども
         
        # ほしいmyformatの抽出        
        for myformat in myformatlist:
            # breakした時点で、myformatに入っている
            if form == 'MOVIE':
                if myformat.movie_id == movie_id:
                    break
            elif form == 'MYLIST':
                if myformat.mylist_id == mylist_id:
                    break
        else: raise ValueError, u'指定されたIDが見つかりません。'
        """
        *アトリビュート上書き
        myformat: 元のmyformat
        edformat: 変更後のmyformat
        """
        edformat = myformat
        if form == 'MOVIE':
            if factor == 'movie_id':
                edformat.movie_id = value
            elif factor == 'movie_name':
                edformat.movie_name = value
            elif factor == 'movie_path':
                edformat.movie_path = value
            elif factor == 'movie_size':
                edformat.movie_size = value
            elif factor == 'priority':
                edformat.priority = value
            elif factor == 'state':
                edformat.state = value
            elif factor == 'option':
                edformat.option = value
            elif factor == 'thumbnail':
                edformat.thumbnail = value
            else:  raise ValueError, u'factorが存在しないか不正な値です。'
        elif form == 'MYLIST':
            if factor == 'mylist_id':
                edformat.mylist_id = value
            elif factor == 'mylist_name':
                edformat.mylist_name = value
            elif factor == 'mylist_description':
                edformat.mylist_description = value
            elif factor == 'rss':
                edformat.rss = value
            elif factor == 'downloaded':
                #print 'downloaded'
                if chengedownloaded > 0:
                    edformat.downloaded.append(value)
                elif chengedownloaded < 0:
                    edformat.downloaded.remove(value)
            else:  raise ValueError, u'factorが存在しないか不正な値です。'
        """myformat[]の上書き"""
        # 元の場所
        itemindex = myformatlist.index(myformat)
        # 元のを除外
        myformatlist.remove(myformat)
        # 入れなおす
        myformatlist.insert(itemindex, edformat)
        #print myformatlist
        """myformatの全体の上書き"""
        myformatparent[form][below] = myformatlist
        #print myformatparent[form][below]
        self.save(myformatparent)

    def getmovieIDs(self, down=False):
        u"""
        　　　　ライブラリ内の動画ID一覧
        down: int 0-9
          downに引数でそのレベル内のみの一覧を返す
        return list
        """
        if not(down in range(0,10)) and not(down==False):
            # 引数が想定外
            raise ValueError(u'downは0-9のint')

        lib = self.libopen()
        movies = []
        if down == False:
            for index in xrange(0,10):
                for item in lib['MOVIE'][index]:
                    movies.append(item.movie_id)
        else:
            for item in lib['MOVIE'][down]:
                movies.append(item.movie_id)

        movies.sort(cmp=self.moviecmp)
        return movies

    def getmylistIDs(self, down=False):
        u"""
        　　　　ライブラリ内のマイリスID一覧
        down: int 0-9
          downに引数でそのレベル内のみの一覧を返す
        return list
        """
        if not(down in range(0,10)) and not(down==False):
            # 引数が想定外
            raise ValueError(u'downは0-9のint')

        lib = self.libopen()
        mylists = []
        if down == False:
            for index in xrange(0,10):
                for item in lib['MYLIST'][index]:
                    mylists.append(item.mylist_id)
        else:
            for item in lib['MYLIST'][down]:
                mylists.append(item.mylist_id)
                
        mylists.sort(cmp=self.mylistcmp)
        return mylists

    def rsscheck(self):
        """
        *ライブラリ内のマイリストについて
        webのマイリストと比較し未DL動画があればライブラリに追加
        """
        items = self.libopen()["MYLIST"]
        for index in xrange(0,10):
            for item in items[index]:
                print u"RSS:", item.mylist_id
                downloaded = item.downloaded
                try:
                    niconicovideo = nicovideoAPI.Nicovideo(mylist_id=item.mylist_id)
                except:  # 接続失敗
                    print u"ニコニコ動画に接続失敗"
                    return False
                movies = niconicovideo.get_mylist_movies()
                #print movies
                for movie in movies:
                    #print '*****************************'
                    try:
                        downloaded.index(movie)
                        continue
                    except ValueError:
                        # movie_idがdownloadedにないとき
                        """
                        myform_m: 登録済みIDリスト
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
        return True
    
    def filenamecheck(self, filename, substitute=u'_'):
        """文字列内にファイル名として不適切な文字があった場合に書き換える
           filename: チェックしたい文字列(unicode)
           substitute: 置き換える文字列
        """
        ed = u''
        for letter in filename:
            if letter in [u'\\', u'/', u':', u'*', u'|', u'<', u'>', u'?']:
                letter = substitute
            ed = ed + letter
        return ed
         
    def moviecmp(self, item1, item2):
        return cmp(int(item1[2:-1]), int(item2[2:-1]))
    def mylistcmp(self, item1, item2):
        return cmp(int(item1), int(item2))
    
    
if __name__ == "__main__":
    print os.getcwd()
    va = nicoDL_Various(libraryfilepath=os.getcwd())
    
    #form = va.make_myformat(mylist_id='28198743', mylist_name=u'デモンズソウルRTA',form='MYLIST')
    #va.write_library(form)
    #va.write_library(va.make_myformat(form='MYLIST', mylist_id='1111', mylist_name=u'テストリスト2'))
    #va.write_library(va.make_myformat(form='MOVIE', movie_id='sm9', movie_name=u'テスト動画', state=True))
    #va.write_library(va.make_myformat(form='MOVIE', movie_id='sm0', movie_name=u'テスト動画2', state=True))
    """

    #va.rsscheck()
    
    #key='mylist_name'
    #print va.pickup(mylist_id='28198743', choice=key)
    #va.rewrite_library(factor=key, value='True', mylist_id='28198743')
    #print va.pickup(mylist_id='28198743', choice=key)
    """
    print va.getmovieIDs()
    print va.getmylistIDs()
    print va.filenamecheck('******`.\`＇\**')

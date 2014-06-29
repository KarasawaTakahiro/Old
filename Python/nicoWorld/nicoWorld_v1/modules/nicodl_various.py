#!/usr/bin/env python
#coding: utf-8

import imaplib
import formats
import nicovideoAPI
import os
import re

class nicoDL_Various():
    def __init__(self, log, libraryfilepath, libraryfilename):
        u"""
        log             : log用のウィンドウobj
        libraryfilepath : ライブラリファイルのある場所
        """
        self.log = log
        self.formats = formats.LibraryFormat(libraryfilepath, libraryfilename)
        self.libraryfilename = libraryfilename
        self.libraryfilepath = libraryfilepath
        self.libraryfile = os.path.join(libraryfilepath, libraryfilename)

    def reloadmoviedata(self, myformat):
        """動画情報を取得する"""
        api = nicovideoAPI.Nicovideo(movie_id=myformat.ID)
        for item in dir(self.formats.getMovieMyformat(movie_id=myformat.ID)):
            if item == 'title':
                self.formats.rewrite(myformat, factor='title', value=api.get_movie_title())
            elif item == 'description':
                self.formats.rewrite(myformat, factor='description', value=api.get_movie_description())
                
            else:  continue

    def reloadmylistdata(self, myformat):
        """マイリス情報を取得する"""
        api = nicovideoAPI.Nicovideo(mylist_id=myformat.ID)
        for item in dir(self.formats.getMylistMyformat(mylist_id=myformat.ID)):
            if item == 'title':
                self.formats.rewrite(myformat, factor='title', value=api.get_mylist_title())
            elif item == 'description':
                self.formats.rewrite(myformat, factor='description', value=api.get_mylist_description())
                
            else:  continue

    def rsscheck(self, mylist_obj):
        """
        *ライブラリ内のマイリストについて
        webのマイリストと比較し未DL動画があればライブラリに追加
        """
        self.formats.load()
        #self.log.write(u"RSS: %s"%mylist_obj.ID)
        try:  api = nicovideoAPI.Nicovideo(mylist_id=mylist_obj.ID)
        except:  # 接続失敗
            self.log.write(u"ニコニコ動画への接続に失敗したため処理を中止します。")
            return False
        movies = api.get_mylist_movies()
        #print 'movies:', movies
        appended = []  # 追加したmovieformatを返すため
        for movieID in movies:
            #print '*****************************'
            try:
                movie_obj = self.formats.getMovieMyformat(movie_id=movieID)  # movie_idが見つからないとValueErrorが出る
                if movie_obj:
                    # マイリスト情報を上書き
                    if movie_obj.mylist_id == mylist_obj.ID:
                        continue
                    else:  # 情報を書き換え
                        self.formats.rewrite(myformat=movie_obj, factor='mylist_id', value=mylist_obj.ID)
                        continue
            except ValueError:
                # movie_idがcatalogにないとき  == 未登録
                """登録
                movie : 追加したいmovie_id
                """
                api_movie = nicovideoAPI.Nicovideo(movie_id=movieID)
                title = api_movie.get_movie_title()
                self.log.write(u'RSSHit: %s: %s'% (movieID, title))
                newmovieformat = self.formats.mkMovieFormat(ID=movieID, title=title, mylist_id=mylist_obj.ID)
                self.formats.append(newmovieformat)
                self.formats.rewrite(myformat=mylist_obj, factor='catalog', value=[movieID])
                appended.append(newmovieformat)
            self.reloadmoviedata(self.formats.getMovieMyformat(movie_id=movieID))
        return appended

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

    def find(self, text):
        u"""
        textからmyformatを返す
        textからマイリスが見つかった時はMylist_Search.MylistSearch.main()

        return
         *それぞれのmyformat

        *見つからない: False
        """
        #print '--- find() -----------------------------'
        #print type(text)
        patt = re.compile('sm\d+')
        matched = patt.search(text)  # videoID検索
        #matched = re.search('sm\d+', text)  # videoID検索
        #print 'find() matched videoID: %s' % matched ###
        if matched:
            video_id = matched.group()
            self.log.write('Hit!: %s' % video_id)
            myformat = self.formats.mkMovieFormat(ID=video_id)
            #print '--- /find() ----------------------------'
            #print ##
            return myformat

        matched = re.search('mylist/\d+', text)  # mylistID検索
        #print 'find() matched mylistID: %s' % matched ###
        if matched:
            mylist_id = matched.group().strip('mylist/')
            self.log.write('Hit! : %s' % mylist_id)
            myformat = self.formats.mkMylistFormat(ID=mylist_id)
            #print '--- /find() ----------------------------'
            #print ##
            return myformat

        #print '--- /find() ----------------------------'
        #print ##
        return False

    def geturl(self, gmailID, gmailPW):
        u"""
        Gmailにアクセスしメールから本文取得
        """

        #print ##

        #print "Gmail ID:",self.gmail_id
        #print "Gmail PW:",self.gmail_pw

        imap = imaplib.IMAP4_SSL('imap.gmail.com')
        imap.login(gmailID, gmailPW)  # Gmail login
        imap.select()

        _, [data] = imap.search(None, 'ALL')
        for i in data.split(' '):
            _, sub = imap.fetch(i, '(RFC822.TEXT)')
            text = sub[0][1].strip()  # メール本文すべて
            myformat = self.find(text)
            if myformat != False:
                imap.store(i, '+FLAGS', '\Deleted')  # メール削除
                imap.logout()
                return myformat
            else: continue

        imap.logout()
        return False


if __name__ == "__main__":
    #print os.getcwd()
    va = nicoDL_Various(True, libraryfilepath=os.getcwd())
    '''
    myformat = formats.LibraryFormat()
    
    #form = va.make_myformat(mylist_id='28198743', mylist_name=u'デモンズソウルRTA',form='MYLIST')
    #va.write_library(form)"""
    myformat.append(myformat.mkMylistFormat(ID='29778453'))
    print myformat.getMylistMyformat('29778453')
    va.rsscheck(myformat.mkMylistFormat(ID='29778453'))
    """
    #key='mylist_name'
    #print va.pickup(mylist_id='28198743', choice=key)
    #va.rewrite_library(factor=key, value='True', mylist_id='28198743')
    #print va.pickup(mylist_id='28198743', choice=key)
    """
    print myformat.getAllMovieMyformat()
    print myformat.getAllMylistMyformat()'''
    
    print va.find(u'http://www.nicovideo.jp/watch/sm17024615')#.encode())

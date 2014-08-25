#!/usr/bin/env python
#coding: utf-8

import imaplib
#from nicoLoad_database import Database
import nicovideoAPI
import os
import re


class nicoLoad_Various():
    def __init__(self, databaseObj, logging):
        u"""
        log             : log用のウィンドウobj
        libraryfilepath : ライブラリファイルのある場所
        """
        self.DB = databaseObj
        self.logging = logging

    def reloadmoviedata(self, movieid):
        """動画情報を取得する"""
        api = nicovideoAPI.Nicovideo(movie_id=myformat.ID)

    def reloadmylistdata(self, movieid):
        """マイリス情報を取得する"""
        api = nicovideoAPI.Nicovideo(mylist_id=myformat.ID)

    def rsscheck(self, mylistid):
        """
        *ライブラリ内のマイリストについて
        webのマイリストと比較し未DL動画があればライブラリに追加
        """
        try:  api = nicovideoAPI.Nicovideo(mylist_id=mylistid)
        except:  # 接続失敗
            print(u"ニコニコ動画への接続に失敗したため処理を中止します。")
            return False
        #print 'movies:', movies
        appended = []  # 追加したmovieidを返すため
        for movieid in api.get_mylist_movies():
            """
            マイリスに登録済みなら何もしない
            未登録なら、マイリスに登録後、動画の情報も追加登録する
            """
            if not(mylistid in self.DB.getMylistHasMovieFromMovie(movieid)):
                self.DB.addMylistHasMovie(mylistid, movieid)
                self.DB.addMovie(movieid)
                print "RSS: %s: %s" % (movieid, api_movie.get_movie_title())
                appended.append(movieid)
        return appended

    def filenamecheck(self, filename):
        """文字列内にファイル名として不適切な文字があった場合に書き換える
           filename: チェックしたい文字列(unicode)
           substitute: 置き換える文字列
        """
        for letter in [("\\", "￥"), ("/", "／"), (":", "："), ("*", "＊"), ("|", "｜"), ("<", "＜"), (">", "＞"), ("?", "？")]:
            filename.replace(letter[0], letter[1])
        return filename

    def find(self, text):
        u"""
        textからidを返す
        textからマイリスが見つかった時はMylist_Search.MylistSearch.main()

        return
         *それぞれのid

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
            self.logging('HitMovie!: %s' % video_id)
            #print '--- /find() ----------------------------'
            #print ##
            return video_id

        matched = re.search('mylist/\d+', text)  # mylistID検索
        #print 'find() matched mylistID: %s' % matched ###
        if matched:
            mylist_id = matched.group().strip('mylist/')
            self.logging('HitMylist! : %s' % mylist_id)
            #print '--- /find() ----------------------------'
            #print ##
            return mylist_id

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
            mmid = self.find(text)
            if mmid != False:
                imap.store(i, '+FLAGS', '\Deleted')  # メール削除
                imap.logout()
                return mmid
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

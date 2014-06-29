#!/usr/bin/env python
#-*- coding: utf-8 -*-

import cgi
import cookielib
import time
import os
import urllib
import urllib2
import urlparse
import re
import wx
import xml.sax.saxutils as saxutils

from BeautifulSoup import BeautifulStoneSoup  # for XML



class Nicovideo():
    u"""
    ニコニコ
    """
    def __init__(self, mylist_id=False, movie_id=False):
        u"""
        mylist_id, movie_id は必要に応じて渡す
        """
        self.movie_id = movie_id
        self.mylist_id = mylist_id

        if mylist_id != False:
            url_rss = 'http://www.nicovideo.jp/mylist/%s?rss=2.0' % str(mylist_id)
            result = urllib2.urlopen(url_rss)
            self.mylist_soup = BeautifulStoneSoup(result.read())  # XMLファイル
        if movie_id != False:
            url_movie = "http://ext.nicovideo.jp/api/getthumbinfo/%s" % str(movie_id)
            result = urllib2.urlopen(url_movie)
            self.movie_soup = BeautifulStoneSoup(result.read())  # XMLファイル

    def get_movie_title(self):
        """
        movie_id を渡す.
        動画名を返す.
        """
        time.sleep(0.1)
        try:
            raw_movie_title = u"".join(self.movie_soup.find('title').contents)
        except AttributeError:
            raw_movie_title = str(self.movie_id)
        movie_title = saxutils.unescape(raw_movie_title, {'&amp;#039;': "'"})  # 文字変換
        # ファイル名に使用不可の文字を除外
        for i in [ur'*:<>?"|/\\']:
            movie_title = movie_title.replace(i, "-")
        return movie_title

    def get_movie_description(self):
        """
        movie_id を渡す.
        動画説明を返す.
        """
        time.sleep(0.1)
        movie_description = u"".join(self.movie_soup.find('description').contents)
        return movie_description

    def get_movie_length(self):
        """
        movie_id を渡す.
        動画時間を返す.
        """
        time.sleep(0.1)
        movie_length = u"".join(self.movie_soup.find('length').contents)
        return movie_length

    def get_mylist_name(self):
        """
        mylist_id を渡す.
        マイリス名を返す.
        """
        time.sleep(0.1)
        mylist_name = u"".join(self.mylist_soup.find('title').contents)
        mylistname = saxutils.unescape(mylist_name, {'&amp;#039;': "'"})
        return mylistname

    def get_mylist_description(self):
        """
        mylist_id を渡す.
        マイリス説明を返す.
        """
        time.sleep(0.1)
        mylist_description = u"".join(self.mylist_soup.find('description').contents)
        return mylist_description

    def save_thumbnail(self, directory):
        """
        movie_id を渡す.
        directory にはサムネ保存フォルダを渡す.
        保存フォルダが無ければ作成
        (directory\data\thumbnail にサムネ保存.)
        サムネの絶対パスを返す.
        """
        time.sleep(0.1)
        savedir = directory #os.path.join(directory, "data", "thumbnail")
        if os.path.exists(savedir) == False:
            os.mkdir(savedir)

        location = u"".join(self.movie_soup.find('thumbnail_url').contents)
        name = re.search("i=\d+", location).group().strip("i=")

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        res = opener.open(location)
        data = res.read()
        ext = res.info().getsubtype()
        path = os.path.join(savedir, "".join([name,".",ext]))
        ofh = open(path ,"wb")
        ofh.write(data)
        ofh.close()

        return path

    def get_movie_size_high(self):
        """
        movie_id を渡す.
        高画質時の動画サイズ(int)を返す.
        """
        time.sleep(0.1)
        movie_size_high = u"".join(self.movie_soup.find('size_high').contents)
        print movie_size_high
        return int(movie_size_high)

    def get_movie_size_low(self):
        """
        movie_id を渡す.
        低画質時の動画サイズ(int)を返す.
        """
        time.sleep(0.1)
        movie_size_low = u"".join(self.movie_soup.find('size_low').contents)
        print movie_size_low
        return int(movie_size_low)

    def get_movie_type(self):
        """
        movie_id を渡す.
        動画の拡張子を返す.
        """
        time.sleep(0.1)
        movie_type = u"".join(self.movie_soup.find('movie_type').contents)
        return movie_type

    def get_view_counter(self):
        """
        movie_id を渡す.
        動画の閲覧数(int)を返す.
        """
        time.sleep(0.1)
        view_counter = u"".join(self.movie_soup.find('view_counter').contents)
        return int(view_counter)

    def get_comment_num(self):
        """
        movie_id を渡す.
        動画のコメ数(int)を返す.
        """
        time.sleep(0.1)
        comment_num= u"".join(self.movie_soup.find('comment_num').contents)
        return int(comment_num)

    def get_mylist_counter(self):
        """
        movie_id を渡す.
        動画のマイリス数(int)を返す.
        """
        time.sleep(0.1)
        mylist_counter = u"".join(self.movie_soup.find('mylist_counter').contents)
        return int(mylist_counter)

    def get_last_res_body(self):
        """
        movie_id を渡す.
        動画のラスコメを返す.
        """
        time.sleep(0.1)
        last_res_body = u"".join(self.movie_soup.find('last_res_body').contents)
        return last_res_body

    def get_tags(self):
        """
        movie_id を渡す.
        動画のタグ（list）を返す.
        """
        time.sleep(0.1)
        tags = []
        tags_child = self.movie_soup.find('tags').findAll('tag')
        for item in tags_child:
            tags.append(unicode(item.string))
            #print unicode(item.string)
        return tags

    def get_user_id(self):
        """
        movie_id を渡す.
        動画の投稿者IDを返す.
        """
        time.sleep(0.1)
        user_id = u"".join(self.movie_soup.find('user_id').contents)
        return user_id

    def get_storageURL(self):
        #ログイン
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        req = urllib2.Request("https://secure.nicovideo.jp/secure/login")
        req.add_data( urllib.urlencode( {"mail":nicovideo_id, "password":nicovideo_pw} ))
        res = opener.open(req)
        #動画配信場所取得(getflv)
        res = opener.open("http://flapi.nicovideo.jp/api/getflv/"+self.movie_id).read()
        videoURL = cgi.parse_qs(res)["url"][0]
        return videoURL

    def save_movie(self, nicovideo_id, nicovideo_pw, directory, mylist=None):
        """
        movie_id を渡しておく.
        mylist : マイリス名を渡す。保存場所にする。マイリスRSSから呼ばれた時用。
        """
        time.sleep(0.1)
        if mylist != None:
            savedir = os.path.join(directory, mylist)
            mylist_flag = True
        else:
            savedir = directory
            mylist_flag = False

        #try:
        # タイトル取得
        title = self.get_movie_title()
        #ログイン
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        req = urllib2.Request("https://secure.nicovideo.jp/secure/login")
        req.add_data( urllib.urlencode( {"mail":nicovideo_id, "password":nicovideo_pw} ))
        res = opener.open(req)
        #動画配信場所取得(getflv)
        res = opener.open("http://flapi.nicovideo.jp/api/getflv/"+self.movie_id).read()
        videoURL = cgi.parse_qs(res)["url"][0]
        #動画のダウンロード
        ##opener.open("http://www.nicovideo.jp/watch/"+self.movie_id)
        res = opener.open(videoURL)
        data = res.read()
        ext = res.info().getsubtype()

        for i in [ur'*:<>?"|/\\']:  # ファイル名に使用不可記号の除外
            title = title.replace(i, "_")
        #print title

        filename = os.path.join(savedir, title+"."+ext)
        ofh = open(filename,"wb")
        ofh.write(data)
        ofh.close()

        return filename

    def get_mylist_movies(self):
        u"""
        mylist_id を渡しておく

        RSS フィードからマイリスに含まれる動画 ID を取得し、
        smIDのリストを返す

        return
         [movieID, movieID, movieID, ・・・・]
        """
        #print 'Run get_mylist_movies'

        idlists = []  # 親リスト
        try:
            url = 'http://www.nicovideo.jp/mylist/%s?rss=2.0' % str(self.mylist_id)
            result = urllib2.urlopen(url)
            soup = BeautifulStoneSoup(result.read())

            for item in soup('item'):  # <item> ~ </item>
                title = item.title.string  # <title> ~ </title> タイトル取得
                link = item.link.string  # <link> ~ </link>
                matched = re.compile('s[mo]\d+').search(link)
                if not matched:
                    continue
                smid = matched.group()  # 'sm000' or 'so000' or 'nm000'
                idlists.append(smid)

                time.sleep(0.1)  # Sleep 0.1 sec

        except:
            return False

        return idlists



if __name__ == '__main__':
    #import os
    #c = Nicovideo(mylist_id = 6628597)
    #print c.mylist_movies()
    #print a.mylist_soup
    #print "*************************************"
    a = Nicovideo(movie_id = u"sm3262156")
    print a.get_tags()
    #print a.movie_soup
    """
    b = a.save_movie('zeuth717@gmail.com', "kusounkobaka", os.getcwd())
    print b

    print a.get_movie_title()
    print a.get_movie_description()
    print a.get_movie_length()
    print "*************************************"
    """
    """
    print c.get_mylist_name()
    print c.get_mylist_description()"""


#http://www.nicovideo.jp/watch/sm16133185




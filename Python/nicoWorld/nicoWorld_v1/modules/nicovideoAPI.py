# coding: utf-8

import cgi
import cookielib
import time
import os
import urllib
import urllib2
#import urlparse
import re
import xml.sax.saxutils as saxutils

from BeautifulSoup import BeautifulSoup  # for XML



class Nicovideo():
    u"""
    *ニコニコ
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
            self.mylist_soup = BeautifulSoup(result.read())  # XMLファイル
        if movie_id != False:
            url_movie = "http://ext.nicovideo.jp/api/getthumbinfo/%s" % str(movie_id)
            result = urllib2.urlopen(url_movie)
            self.movie_soup = BeautifulSoup(result.read())  # XMLファイル
        
    def get_movie_title(self):
        """
        movie_idを渡す
        *動画名を返す
        """
        time.sleep(0.1)
        try:
            raw_movie_title = u"".join(self.movie_soup.find('title').contents)
        except AttributeError:
            raw_movie_title = str(self.movie_id)
            # 文字変換
        movie_title = saxutils.unescape(raw_movie_title, {'&amp;#039;': "'",
                                                          '&quot;':'"',
                                                          '&amp;':'&',
                                                          '&gt;':u'＞'
                                                          })
        return movie_title

    def get_movie_description(self):
        """
        movie_idを渡す
        *動画説明
        """
        time.sleep(0.1)
        movie_description = u"".join(self.movie_soup.find('description').contents)
        return movie_description

    def get_movie_length(self):
        """
        movie_idを渡す
        *動画時間を返す
        """
        time.sleep(0.1)
        movie_length = u"".join(self.movie_soup.find('length').contents)
        return movie_length

    def get_mylist_title(self):
        """
        mylist_idを渡す
        *マイリス名を返す
        """
        time.sleep(0.1)
        mylist_name = u"".join(self.mylist_soup.find('title').contents)
        mylistname = saxutils.unescape(mylist_name, {'&amp;#039;': "'"})
        if type(mylistname) == type(u''):
            mylistname = mylistname[6:-7]
        return mylistname

    def get_mylist_description(self):
        """
        mylist_idを渡す
        *マイリス説明を渡す
        """
        time.sleep(0.1)
        mylist_description = u"".join(self.mylist_soup.find('description').contents)
        return mylist_description

    def save_thumbnail(self, savedir, name=False):
        """
        movie_idを渡す
        savedir: 保存フォルダ
        name: サムネのファイル名
        return
         *ファイル名
        *保存フォルダがなければ作成
        *サムネの絶対パスを返す
        """
        time.sleep(0.1)
        #os.path.join(directory, "data", "thumbnail")
        if os.path.exists(savedir) == False:
            #print 'mkdir' 
            os.makedirs(savedir)
            #os.mkdir(savedir)
        # 保存IRL取得
        location = u"".join(self.movie_soup.find('thumbnail_url').string)
        # ファイル名決定
        if not name:
            # ファイル名が与えられてないとき
            name = re.search("i=\d+", location).group().strip("i=")

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        res = opener.open(location)
        data = res.read()
        ext = res.info().getsubtype()
        path = os.path.join(savedir, u"".join([name,".",ext]))
        ofh = open(path ,"wb")
        ofh.write(data)
        ofh.close()

        return path

    def get_movie_size_high(self):
        """
        movie_idを渡す
        *高画質時の動画サイズを返す
        """
        time.sleep(0.1)
        movie_size_high = u"".join(self.movie_soup.find('size_high').contents)
        #print movie_size_high
        return int(movie_size_high)

    def get_movie_size_low(self):
        """
        movie_idを渡す
        *低画質時の動画サイズ(int)を返す
        """
        time.sleep(0.1)
        movie_size_low = u"".join(self.movie_soup.find('size_low').contents)
        #print movie_size_low
        return int(movie_size_low)

    def get_movie_type(self):
        """
        movie_idを渡す
        *動画の拡張子を返す
        """
        time.sleep(0.1)
        movie_type = u"".join(self.movie_soup.find('movie_type').contents)
        return movie_type
    
    def get_comment(self, nicovideo_id, nicovideo_pw, fig=500):
        """
        *動画IDわたす
        *コメントをxml形式で返す
        fig: 取得するコメント数  1~1000のint
        """
        if not(1<=fig<=1000): raise ValueError, 'figは1~1000の値にしてください'
        # ログイン
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        req = urllib2.Request("https://secure.nicovideo.jp/secure/login")
        req.add_data(urllib.urlencode({"mail":nicovideo_id, 
                                        "password":nicovideo_pw}))
        opener.open(req)
        # API getflv
        res = opener.open("http://flapi.nicovideo.jp/api/getflv/"+self.movie_id).read()
        thread_id = cgi.parse_qs(res)['thread_id'][0]
        ms = cgi.parse_qs(res)['ms'][0]
        #print ms  # サーバー
        #print thread_id  # thread ID

        req = urllib2.Request(ms)
        res = opener.open(ms+'thread?'+urllib.urlencode( {"thread":thread_id, 'version':"20061206", 'res_from':'-%i'%fig} ))
        return res.read()

    def save_comment(self, nicoID, nicoPW, savedir, filename, fig=500):
        """
        savedir: 保存場所
        filename: ファイル名（拡張子を除く）
        fig: 取得するコメント数(1~1000)
        """
        comment = self.get_comment(nicoID, nicoPW, fig)
        filename = os.path.join(savedir, filename+'.xml')
        ff = open(filename, 'w')
        ff.write(comment)
        ff.close()
        return filename

    def get_view_counter(self):
        """
        movie_idを渡す
        *動画の閲覧数を返す
        """
        time.sleep(0.1)
        view_counter = u"".join(self.movie_soup.find('view_counter').contents)
        return int(view_counter)

    def get_comment_num(self):
        """
        movie_idを渡す
        *動画のコメ数(int)を返す
        """
        time.sleep(0.1)
        comment_num= u"".join(self.movie_soup.find('comment_num').contents)
        return int(comment_num)

    def get_mylist_counter(self):
        """
        movie_idを渡す
        *動画のマイリス数を渡す
        """
        time.sleep(0.1)
        mylist_counter = u"".join(self.movie_soup.find('mylist_counter').contents)
        return int(mylist_counter)

    def get_last_res_body(self):
        """
        movie_idを渡す
        *動画のラスコメを返す
        """
        time.sleep(0.1)
        last_res_body = u"".join(self.movie_soup.find('last_res_body').contents)
        return last_res_body

    def get_tags(self):
        """
        movie_idを渡す
        *動画のダグ(list)を返す
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
        movie_idを渡す
        *投稿者IDを返す
        """
        time.sleep(0.1)
        user_id = u"".join(self.movie_soup.find('user_id').contents)
        return user_id

    def get_storageURL(self, nicovideo_id, nicovideo_pw):
        #ログイン
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        req = urllib2.Request("https://secure.nicovideo.jp/secure/login")
        req.add_data( urllib.urlencode( {"mail":nicovideo_id, "password":nicovideo_pw} ))
        res = opener.open(req)
        #動画配信場所取得(getflv)
        res = opener.open("http://flapi.nicovideo.jp/api/getflv/"+self.movie_id).read()
        videoURL = cgi.parse_qs(res)["url"][0]
        return videoURL

    def save_movie(self, nicovideo_id, nicovideo_pw, savedir):
        """
        movie_id を渡しておく
        return path
        """
        time.sleep(0.1)
        # タイトル取得
        title = self.get_movie_title()
        #ログイン
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        req = urllib2.Request("https://secure.nicovideo.jp/secure/login")
        req.add_data( urllib.urlencode( {"mail":nicovideo_id, "password":nicovideo_pw} ))
        res = opener.open(req)
        # 動画配信場所取得(getflv)
        videoURL = self.get_storageURL(nicovideo_id=nicovideo_id, nicovideo_pw=nicovideo_pw)
        # 動画のダウンロード
        opener.open("http://www.nicovideo.jp/watch/"+self.movie_id)
        res = opener.open(videoURL)
        data = res.read()
        ext = res.info().getsubtype()

        for i in [ur'*:<>?"|/\\']:  # ファイル名に使用不可文字列を除外
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
        
        RSSフィードからマイリスに含まれる動画IDを取得し、
        *動画IDのリストを返す
        
        return
         [movieID, movieID, movieID, ・・・・]
        """
        #print 'Run get_mylist_movies'

        idlists = []  # 親リスト
        url = 'http://www.nicovideo.jp/mylist/%s?rss=2.0' % str(self.mylist_id)
        result = urllib2.urlopen(url)
        soup = BeautifulSoup(result.read())

        for item in soup.findAll('item'):  # <item> ~ </item>
            matched = re.compile('sm\d+').search(str(item))
            if not matched:
                continue
            smid = matched.group()  # 'sm000'
            idlists.append(smid)

            time.sleep(0.1)  # Sleep 0.1 sec


        return idlists

    def logintest(self, ID, PW):
        """
        login失敗でFalse
        """
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        req = urllib2.Request("https://secure.nicovideo.jp/secure/login")
        req.add_data( urllib.urlencode( {"mail":ID, "password":PW} ))
        res = opener.open(req)
        
        if not res.headers.getaddr('x-niconico-id')[1]:
            return False
        else:
            return True
        
if __name__ == '__main__':
    #import os
    #c = Nicovideo(mylist_id = 28198743)
    c = Nicovideo(mylist_id = 30309865)
    name = c.get_mylist_name()
    print name#[6:-7]
    #print len(name[6:-7])
    #print c.get_mylist_movies()
    #print a.mylist_soup
    #print "*************************************"
    #a = Nicovideo(movie_id = u"sm3262156")
    #print a.get_tags()
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




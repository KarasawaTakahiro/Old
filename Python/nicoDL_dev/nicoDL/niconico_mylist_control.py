#!/usr/bin/env python
#-*- coding: utf-8 -*-

u"""
奴隷王マイリス
http://www.nicovideo.jp/mylist/13888887?rss=2.0
なんか作ったやつ (18)
http://www.nicovideo.jp/mylist/6628597?rss=2.0
単発＆オマケ＆短いシリーズの実況っぽいプレイ動画 (12)
http://www.nicovideo.jp/mylist/8564672?rss=2.0
バッソ
http://www.nicovideo.jp/mylist/20399676
"""

import os
import os.path
import re
import time
import urllib2
import xml.sax.saxutils as saxutils
from BeautifulSoup import BeautifulStoneSoup  # for XML


class MylistControl():
    u"""
    マイリス管理
    """
    def __init__(self, directory, rss=None, debug=False):
        u"""
        rss: マイリスID
        directory: 保存場所
        """

        self.mylist_id = rss

        if not rss == None:
            self.url = 'http://www.nicovideo.jp/mylist/%s?rss=2.0' % str(rss)
            result = urllib2.urlopen(self.url)
            self.soup = BeautifulStoneSoup(result.read())
            self.mylistname()  # 必要 マイリスを使えるようにする

        self.directory = directory

        if debug:
            self.backuptxt = os.path.join(self.directory, 'data\\test2_backup.txt')
        elif not debug:
            self.backuptxt = os.path.join(self.directory, 'data\\backup.txt')

        self.txtdir = os.path.join(self.directory, 'control')  # 管理用txt保存フォルダ
        if not os.path.exists(self.txtdir):  # 無ければ作成
            os.mkdir(self.txtdir)
        self.directory = os.path.join(self.directory, 'control')

        self.rssdir = os.path.join(self.directory, 'RSS.txt')
        if not os.path.exists(self.rssdir):  # RSSファイル
            f = open(self.rssdir, 'a')
            f.close()

        self.debug= debug



    def parse_feed(self, mylist_id, display=True):
        u"""
        RSS フィードからマイリスに含まれる動画 ID を取得し、
        smIDのリストを返す
        display: URL,タイトルを表示するか

        return
         [[smID, movie_name], [smID, movie_name], ・・・・]
        """
        #print 'Run parse_feed'

        print self.url
        movie_url = 'http://www.nicovideo.jp/watch/'
        idlists = []  # 親リスト
        try:

            url = 'http://www.nicovideo.jp/mylist/%s?rss=2.0' % str(mylist_id)
            result = urllib2.urlopen(self.url)
            soup = BeautifulStoneSoup(result.read())

            for item in self.soup('item'):  # <item> ~ </item>
                title = item.title.string  # <title> ~ </title> タイトル取得
                link = item.link.string  # <link> ~ </link>
                matched = re.compile('s[mo]\d+').search(link)
                if not matched:
                    continue
                sm = matched.group()  # 'sm000' or 'so000' or 'nm000'
                idlists.append(smids)
                mess = '%s\n->%s' % (''.join([movie_url, sm]), str(mylist_id))
                if display:
                    print mess

                time.sleep(0.1)  # Sleep 0.1 sec

        except e:
            print e
        #idlists.reverse()  # 自由
        return idlists






# webから読み込み関数群
    def mylistname(self):
        """
        マイリス名取得
        """
        self.mylist_title = ''.join(self.soup.find('title').contents)  # マイリスト名
        self.mylist_title = saxutils.unescape(self.mylist_title, {'&amp;#039;': "'"})#, '&gt':'>'})
        print self.mylist_title
        return self.mylist_title

    def get_title(self, url):

        result = urllib2.urlopen(url)
        stonesoup = BeautifulStoneSoup(result.read())
        tag = stonesoup.find('title')
        if tag:
            title = tag.text
            return title
        return u'取得失敗'

    def parse_feed(self, display=True):
        u"""
        RSS フィードからマイリスに含まれる動画 ID を取得し、
        smIDのリストを返す
        display: URL,タイトルを表示するか

        return
         [[smID, movie_name], [smID, movie_name], ・・・・]
        """
        #print 'Run parse_feed'

        print self.url
        movie_url = 'http://www.nicovideo.jp/watch/'
        idlists = []  # 親リスト

        for item in self.soup('item'):  # <item> ~ </item>
            smids = []
            title = item.title.string  # <title> ~ </title> タイトル取得
            link = item.link.string  # <link> ~ </link>
            matched = re.compile('s[mo]\d+').search(link)
            if not matched:
                continue
            sm = matched.group()  # 'sm000' or 'so000' or 'nm000'
            thumbinfo_url = 'http://ext.nicovideo.jp/api/getthumbinfo/' + sm
            smids.append(sm)
            title = self.get_title(thumbinfo_url)
            smids.append(title)
            mess = '%s\n->%s' % (''.join([movie_url, sm]), title)
            idlists.append(smids)
            if display:
                print mess
            #logging.info(mess)

            time.sleep(0.1)  # Sleep 0.1 sec

        return idlists

    def writing(self, dl_flag, movie_id, movie_name):
        #print 'Run writing'

        #print '--- writeing() ------------'
        #print dl_flag, movie_id, movie_name ##
        self.txtfile.write('%s;%s;%s\n' % (str(dl_flag), movie_id, movie_name))
        print 'writing: %s' % movie_id
        time.sleep(0.1)
        #print '--- /writeing() -----------'

    def mk_management_txt(self):
        u"""
        マイリス管理txt作成
        """
        #print 'Run mk_management_txt'

        #print self.txtdir ##

        mylist_title_filename = []   # ファイル名に使えない文字列除去
        for i in list(self.mylist_title):
            if i == ';':
                i = '_'
            mylist_title_filename.append(i)
        mylist_title_filename = ''.join(mylist_title_filename)  # ここまで

        self.txtfile = open(os.path.join(self.txtdir, ''.join([mylist_title_filename, '.txt'])), 'w')  # 管理用txt
        u"""
        上記のファイル階層
        niconicoDL
         -control (txtdir)
          -管理用txtファイル (txtfile)
        """

        feed = self.parse_feed()
        for lists in feed:
            self.writing(u'F', lists[0], lists[1])

        self.txtfile.close()  # 必要
        print
        time.sleep(1)
# webから読み込み関数群　ここまで

if __name__ == '__main__':
    d = os.getcwd()

    #control = MylistControl(d, 20399676, True)
    '''control.writing_function_group()'''

    control = MylistControl(d, 20399676, debug=True)
    control.get_title()
    control.parse_feed()

    print 'End..'


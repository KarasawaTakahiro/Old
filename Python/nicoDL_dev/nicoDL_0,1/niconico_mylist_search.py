#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging
import urllib2
import re
import time
from BeautifulSoup import BeautifulStoneSoup  # for XML

#
# main() -> parse_feed(url) の順に実行
#
class MylistSearch():
    def __init__(self, debug):
        self.debug = debug
        if self.debug:  # デバッグ時
            self.writefile = 'mylist_test.txt'  # 書き出しファイル
            self.writemode = 'w'  # 書き込みモード
            logfile = ''.join([str(datetime.date.today()), '-MylistSeach_test','.txt'])
        else:
            self.writefile = 'backup.txt'
            self.writemode = 'a'
            logfile = ''.join([str(datetime.date.today()), '-MylistSeach','.txt'])

        # logging setting
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(asctime)s]\n%(message)s\n',
                            filename=''.join([r'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\nicoDL\log', '\\', logfile]), # logファイル置き場
                            filemode='a')

    def parse_url(self, url):
        #print url
        result = urllib2.urlopen(url)
        soup = BeautifulStoneSoup(result.read())
        tag = soup.find('title')
        if tag:
            title = tag.text
            return title
        return u'取得失敗'


    # RSS フィードからマイリスに含まれる動画 ID を取得し、リストを返す
    def parse_feed(self, url):
        try:
            result = urllib2.urlopen(url)
            soup = BeautifulStoneSoup(result.read())
            urls = []

            for item in soup('item'):  # <item> ~ </item>
                title = item.title.string  # <title> ~ </title> タイトル取得
                link = item.link.string  # <link> ~ </link>
                #print link ##
                matched = re.compile('s[mo]\d+').search(link)
                if not matched:
                    continue
                sm = matched.group()  # 'sm000' or 'so000' or 'nm000'
                thumbinfo_url = 'http://ext.nicovideo.jp/api/getthumbinfo/' + sm
                url = 'http://www.nicovideo.jp/watch/' + sm
                urls.append(url)
                title = self.parse_url(thumbinfo_url)
                mess = '%s\n->%s' % (url, title)
                print mess
                logging.info(mess)

                time.sleep(0.1)  # Sleep 0.1 sec

            logging.info('++++++++++++++++++++++++++++++++++++++++++')

        except Exception, e:
            print e
        return urls

    def main(self, mylist_id):
        u"""
        mylistIDを渡す
        RSSをたどってURL取得し
        バックアップファイルに書き込みする
        """
        print u'*** niconico_mylist_search() ***********'
        rss = 'http://www.nicovideo.jp/mylist/%s?rss=2.0' % str(mylist_id)
        for a in xrange(10):
            try:
                urllist = self.parse_feed(rss)
                break
            except urllib2.URLError, error:
                print error
                time.sleep(30)
                continue
        f = open(self.writefile, self.writemode)
        for a in urllist:
            f.write(''.join([a,'\n']))
        f.close()
        print u'*** /niconico_mylist_search() **********'

if __name__ == '__main__':
    mylist = MylistSearch(debug=True)
    mylist_id = '13888887' # マイリスID
    mylist.main(mylist_id)
# coding: utf-8

import os
import urllib
import urllib2
import re
import sys
import time
import xml.sax.saxutils as saxutils

from BeautifulSoup import BeautifulSoup

class VocaloidLyrics():
    def __init__(self):
        pass

    def url_convert(self, pageurl):
        symbol = re.compile('page=.*')
        element = symbol.search(pageurl)
        return "http://www5.atwiki.jp/hmiku/?&type=normal&%s" % element.group()

    def search(self, keyword):
        """
        return [(title, LyricsPageURL)]
        """
        elements = []
        try: pageurl = "http://www5.atwiki.jp/hmiku/?cmd=search&keyword=%s&andor=and" % urllib.quote(keyword.encode('utf-8'))  # URLデコード
        except KeyError:  # エラーが出たらデコードせず
            pageurl = "http://www5.atwiki.jp/hmiku/?cmd=search&keyword=%s&andor=and" % keyword
        try:
            result = urllib.urlopen(pageurl)
        except:
            # プロキシ
            result = urllib.urlopen(pageurl, proxies={"http":"http://wwwproxy.kanazawa-it.ac.jp:8080"})
        soup = BeautifulSoup(result.read())  # XMLファイル
        results = soup.findAll('a', attrs={'href':re.compile('cmd=word.')}) #<a href='**cmd=word**'>**</a> で検索
        #fname = 'url2'  #####
        print u"取得完了"
        for link in results:
            #link.string = urllib.unquote(str(link.string)).decode('utf-8')  # デコード
            #link.string = saxutils.unescape(link.string,{'&amp;':'&',  # デコード
            #                                             '&#039;':'`'})
            if link.string.find(u'過去ログ') > -1:  # 除外
                continue
            if link.string.find(u'カラオケ配信曲一覧') > -1:  # 除外
                continue
            if link.string.find(u'曲一覧') > -1:  # 除外
                continue
            """
            link.string: タグ内文字列
            link.attrs: 属性タプルリスト
            """
            #print type(link.string)  ##################
            title = link.text#unicode(str(link.string))  # タイトル
            lyricspageurl = self.url_convert(dict(link.attrs)['href'])  # リンク先

            #elements.append((title, lyricspageurl))
            yield (title, lyricspageurl)

        #return elements

    def getlyrics(self, pageurl):
        """
        return 歌詞(unicode)
        """
        try:
            result = urllib2.urlopen(pageurl)
        except:
            result = urllib.urlopen(pageurl, proxies={"http":"http://wwwproxy.kanazawa-it.ac.jp:8080"})
        soup = BeautifulSoup(result.read().replace('<br />', '').replace('<br>', ''))
        div = soup.findAll('div')

        lyrics = u''
        for item in div:
            text = unicode(str(item.string), 'utf-8').strip('\n')
            #print 'IN :',text
            #time.sleep(0.5)
            # 除外
            if text.find(u'None') >=0:
                continue
            elif text.find(u'メニュー') >= 0:
                continue
            elif text.find(u'データベース') >= 0:
                continue
            elif text.find(u'編集') >= 0:
                continue
            #print 'OUT:',text
            #mywrite(text, fname, 'a')
            lyrics = lyrics + text + '\n'
        return lyrics

    def xgetlyrics(self, pageurl):
        """
        return 歌詞(unicode)
        """
        try:
            result = urllib2.urlopen(pageurl)
        except:
            result = urllib.urlopen(pageurl, proxies={"http":"http://wwwproxy.kanazawa-it.ac.jp:8080"})
        soup = BeautifulSoup(result.read().replace('<br />', '').replace('<br>', ''))
        div = soup.findAll('div')

        lyrics = u''
        for item in div:
            text = unicode(str(item.string), 'utf-8').strip('\n')
            #print 'IN :',text
            #time.sleep(0.5)
            # 除外
            if text.find(u'None') >=0:
                continue
            elif text.find(u'メニュー') >= 0:
                continue
            elif text.find(u'データベース') >= 0:
                continue
            elif text.find(u'編集') >= 0:
                continue
            #print 'OUT:',text
            #mywrite(text, fname, 'a')
            lyrics = text + '\n'
            yield lyrics

if __name__ == "__main__":
    vocaloidlyrics = VocaloidLyrics()
    print vocaloidlyrics.search(u"from")

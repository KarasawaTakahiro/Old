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
        print 'directory:', directory

        if debug:
            self.backuptxt = os.path.join(self.directory, 'test2_backup.txt')
        elif not debug:
            self.backuptxt = os.path.join(self.directory, 'backup.txt')


        self.txtdir = os.path.join(self.directory, 'control')  # 管理用txt保存フォルダ
        if not os.path.exists(self.txtdir):  # 無ければ作成
            os.mkdir(self.txtdir)
        self.directory = os.path.join(self.directory, 'control')

        self.rssdir = os.path.join(self.directory, 'RSS.txt')
        if not os.path.exists(self.rssdir):  # RSSファイル
            f = open(self.rssdir, 'a')
            f.close()

        self.debug= debug

# 参照関数群
    def consultation(self, reference=None, entry=None):
        u"""
        reference: 参照したい文字列
        entry: 登録したい文字列

        .txt
         No:name
        return
            reference: mylistname -> number
            reference: number -> mylistname
            entry: True
            other: False
        """
        #print 'Run Consultation'

        try:
            f = open(os.path.join(self.txtdir, 'reference.txt'), 'r')
        except IOError:  # ファイルがなければ作成
            f = open(os.path.join(self.txtdir, 'reference.txt'), 'w')
            f.write(u'0')
            f.write(u'\n')
            f.close()
            f = open(os.path.join(self.txtdir, 'reference.txt'), 'r')

        try :
            no = f.readline().strip('\n')
            no = int(no)
        except ValueError:#UnicodeDecodeError or ValueError:
            print 'ValueError'
            no = 0
            u"""一行目は次に使うNo"""

        # 参照時
        if not reference == None:
            #print 'reference:', reference

            try:  # 数字で参照時
                int(reference)
                for i in f.readlines():
                    a = i.split(u';')
                    if a[0] == str(reference):
                        f.close()
                        return a[1].strip(u'\n')
            except ValueError:  # 文字列参照時
                for i in f.readlines():
                    #print 'True:',i
                    a = i.split(u';')
                    if a[1].strip(u'\n') == reference:
                        f.close()
                        return a[0]
        # 登録時
        elif not entry == None:
            print 'entry:', entry
            es = []  # 書き込むリスト
            for i in f.readlines():
                es.append(i.strip('\n'))
            u"""かぶり判定"""
            judges = []
            for i in es:
                judges.append(i.split(';'))
            judge = True
            for i in judges:
                if i[1].strip('\n') == entry:
                    judge = False
            if judge == False:
                return True
            u"""ここまで"""
            f = open(os.path.join(self.txtdir, 'reference.txt'), 'w')
            f.write(u''.join([str(no+1), '\n']))
            f.write(u''.join([str(no), u';', entry, u'\n']))
            for i in es:
                f.write(''.join([i, '\n']))
            f.close()
            return True
        else:  # 失敗時
            print u'書き込み失敗'

        if not f.closed:
            f.close()
# 参照関数群　ここまで


# webから読み込み関数群
    def mylistname(self):
        #print 'Run mylistname'

        self.mylist_title = ''.join(self.soup.find('title').contents)  # マイリスト名
        self.mylist_title = saxutils.unescape(self.mylist_title, {'&amp;#039;': "'"})#, '&gt':'>'})
        print self.mylist_title
        return self.mylist_title

    def get_title(self, url):
        #print 'Run get_title'

        #print url
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
        try:
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

            #logging.info('++++++++++++++++++++++++++++++++++++++++++')

        except Exception, e:
            print e
        #idlists.reverse()  # 自由
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

# 読み込み関数群
    def read(self, folder, mylisttxtname, id=None, flag=None):
        u"""
        渡されたマイリスのtxtを読んでFの付いているIDをタプルで返す
        return ((#,ID),(#,ID),(#,ID))
        """
        #print 'Run read'

        folder = os.path.join(self.directory, u''.join([mylisttxtname, u'.txt']))
        #print 'folder:',folder
        index = self.consultation(reference=mylisttxtname)  # index
        f = open(folder, 'r')
        items = f.readlines()
        mylist = []
        for i in items:
            item = []
            #print 'i:',unicode(i)
            try:
                item = i.strip(u'\n').split(u';')
            except UnicodeDecodeError:
                item = i.strip('\n').split(';')
            #print item
            u"""
            item.[0] = T/F
            item.[1] = 動画ID
            item.[2] = タイトル
            """
            if item[0] == u'F':
                mylist.append(('#%s'%index, item[1]))

        return tuple(mylist)
# 読み込み関数群　ここまで

# バックアップファイルに書き込み
    def backup_write(self):
        u"""
        controlフォルダから*.txtを参照して
        Fの付いてるmovieIDをバックアップファイルに#付きで書き込み
        """
        #print 'Run backup_write'

        url =  r'http://www.nicovideo.jp/watch/'
        files = []  # filename

        for dirpath, dirname, filenames in os.walk(self.directory):  # .txt検索
            del dirpath, dirname
        #print filenames

        for i in filenames:
            #print i
            if not type(i) == type(u''):
                i = i.decode('cp932')
            #print i
            if i == 'reference.txt' or i == 'note.txt' or i == 'RSS.txt':
                continue
            files.append(i.split('.')[0])
        #print files

        items = []
        for filename in files:
            #print filename
            for i in self.read(self.directory, filename):
                #print i
                items.append(i)

        f = open(os.path.join(r'.\..', self.backuptxt), 'a')
        #print 'DIR:', os.path.join(r'.\..', self.backuptxt)
        for i in items:
            #print 'i:',i
            f.write(''.join([i[0], ';', url, i[1], '\n']))
        f.close()

        return True
# バックアップファイルに書き込み　ここまで

# フラグ書き換え関数群
    def reflag(self, movieid, poundsign):
        u"""
        items: (funcNo,id)
        """
        #print 'Run reflag'
        #print 'dir:', self.directory

        #print 'movieid:',movieid
        poundsign = re.search('#\d+', poundsign).group().strip('#')
        #print 'poundsign:',poundsign
        filename = self.consultation(reference=poundsign)+'.txt'
        #print filename
        f = open(os.path.join(self.directory, filename), 'r')
        items = f.readlines()
        f.close()

        #print 'items:',items
        after = []
        for i in items:
            i = i.split(';')
            #print 'i[1]:', i[1]
            #print 'movi:',movieid
            #print i[1] == movieid
            if i[1] == movieid:
                i[0] = 'T'
            after.append(';'.join(i))
            #print

        f = open(os.path.join(self.directory,filename), 'w')
        for i in after:
            f.write(i)
            #print 'reflag.writing:', i
        f.close()
# フラグ書き換え関数群　ここまで

# バックアップテキストに書き込みまで
    def writing_function_group(self):
        u"""
        バックアップテキストに書き込みまで

        書き込みたいマイリスIDを渡したインスタンスを作ってからこの関数を使う
        """
        try:
            self.mk_management_txt()
            self.consultation(entry=self.mylist_title)
            self.backup_write()
            #  RSS登録
            old = []  # 登録済みリスト
            f = open(self.rssdir, 'r')
            for i in f:
                old.append(i.strip('\n'))
            f.close()
            flag = True
            for i in old:
                if i == str(self.mylist_id):
                    flag = False
                    break
            if flag == True:
                f = open(self.rssdir, 'a')
                f.write('%s\n'%self.mylist_id)
                f.close()

        except AttributeError:
            raise AttributeError, u'You must first create an instance mylistID handed.'
# バックアップテキストに書き込みまで　ここまで

# RSS機能関数
    def rss(self):
        u"""
        RSS.txt に登録されているIDに対して
        動画の更新がないかを調べて
        あった場合には管理用txtに書き込む

        return
           True
        """
        print u'マイリストの更新を確認します.'
        f = open(self.rssdir)  # RSS.txt 読み込み
        rsses = f.readlines()
        f.close()

        for i in rsses:
            rss = i.strip('\n')
            control = MylistControl(r'.', rss, self.debug)
            new = control.parse_feed(display=False)  # ネット上 movieIDリスト

            txtfile = ''.join([control.mylist_title, '.txt'])
            #print 'txtfile:',txtfile
            f = open(os.path.join(self.directory, txtfile))
            old_p = f.readlines()  # バックアップファイル内　movieIDリスト
            f.close()

            #print 'new:', new
            #print 'old_p:', old_p
            old = []
            for item in old_p:
                old.append(item.split(';'))
            #print 'old:', old
            '''
            new = [['ID', title],['ID', title],***]
            old_p = ['F;ID;title', '*;**;***','*;***;**']
            old = [[F,ID,title],[F,ID,title],[]]
            '''

            enter = []  # 追記リスト
            for item in new:
                '''
                item[0] = ID
                item[1] = title
                '''
                flag = True
                #print item
                for o in old:
                    if o[1] == item[0]:
                        flag = False
                        break
                if flag == True:
                    enter.append(item)
            if len(enter) == 0:
                print u'新しい動画はありません.'
            else:
                print u'更新を確認しました(%i).'%len(enter)
                for a in enter:
                    '''
                    a[0] = ID
                    a[1] = title
                    '''
                    print a[0],a[1]
            print

            if  len(enter) == 0:
                pass
            else:
                f = open(os.path.join(self.directory, control.mylist_title+'.txt'), 'a')
                for item in enter:  # ファイルに書き込み
                    f.write('F;%s;%s\n' % (item[0], item[1]))
                f.close()

        return True

# RSS機能関数 ここまで

if __name__ == '__main__':
    d = r'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\nicoDL'

    #control = MylistControl(d, 20399676, True)
    '''control.writing_function_group()'''

    control = MylistControl(d, debug=True)
    control.rss()
    print 'End..'


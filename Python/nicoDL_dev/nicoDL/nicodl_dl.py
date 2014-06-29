# coding: utf-8

import free_disc_space as freespace
import nicodl_various_beta as Various
import nicodl_sendmail as SendMail
import nicovideo as Nicovideo
import re
import os.path
import pickle
import sys
import time
#import youtube_search as youtube_search

from imaplib import *

class RemoteNicovideoDL():
    def __init__(self, gmailID, gmailPW, nicoID, nicoPW, to_address, savedirectory):  ##
        """
        gmailID
        gmailPW
        nicoID
        nicoPW
        to_address
        savedirectory
        """
        #
        self.cdir = os.getcwd()  # カレントディレクトリ
        self.url_front =  r'http://www.nicovideo.jp/watch/'
        self.myformats = []
        self.empty = True  # emptyメッセージ表示フラグ
        self.message = u'NicoVideoDL'  # GUI表示用
        self.debug = False
        # display
        self.movie_id_display = u"動画ID"
        self.title_display = u"タイトル"
        self.description_display = u"動画説明"
        self.options = u"オプション"
        self.thumbnail_display = False

        self.start_wait_time = 1  # 5分
        self.timeout_wait_time = 1  # 5分
        self.wait_time = 1
        self.empty_wait_time = 3
        info_file = "data\\info.ndl"
        self.backupfile = 'data\\backup.txt'

        # info
        """
        f = open(info_file)
        info = pickle.load(f)
        f.close()
        self.gid = info["gmail_ID"]
        self.gpw = info["gmail_PW"]
        self.nicoid = info["nico_ID"]
        self.nicopw = info["nico_PW"]
        self.toaddr = info["to_addr"]
        self.savedir = info["savedir"]
        """
        self.gid = gmailID
        self.gpw = gmailPW
        self.nicoid = nicoID
        self.nicopw = nicoPW
        self.toaddr = to_address
        self.savedir = savedirectory


    def find(self, text):
        u"""
        text からmyformatを返す.
        text からマイリスが見つかった場合は Mylist_Search.MylistSearch.main() を使用
        text からYouTube動画URLが見つかった場合はYouTubeSearch.YouTubeSearch.main() を使用

        return -1 はメール削除後continue

        return
          動画URL: movie format
          mylist : mylist format
          YouTube:

          other  : False
        """
        nicodl_various = Various.nicoDL_Various()
        print '--- find() -----------------------------'
        #print text
        matched = re.search('[s][mo]\d+', text)  # videoID検索
        #print 'find() matched videoID: %s' % matched ###
        if matched:
            video_id = matched.group()
            print 'Hit!: %s' % video_id ###
            myformat = nicodl_various.make_myformat(movie_id=video_id, state=False)  # movie format
            #print '--- /find() ----------------------------'
            #print ##
            print self, 'myformat:',myformat
            return myformat

        matched = re.search('mylist/\d+', text)  # mylistID検索
        #print 'find() matched mylistID: %s' % matched ###
        if matched:
            mylist_id = matched.group().strip('mylist/')
            print 'Hit! mylistID: %s' % mylist_id ###
            myformat = nicodl_various.make_myformat(mylist_id=mylist_id)  # mylist format
            #print 'Waiting...'
            time.sleep(0.1)
            #print '--- /find() ----------------------------'
            #print ##
            return myformat

        """ YOU TUBE
        matched = re.search('v=\w+', text)  # YouTube検索 #youtube.com/watch?
        #print 'find() matched youtube_videoID: %s' % matched
        if matched:
            youtube_video_id = matched.group().strip('v=')
            print 'Hit! mylistID: %s' % youtube_video_id ###
            youtubesearch = youtube_search.YouTubeSearch(self.debug)
            youtubesearch.main(youtube_video_id)
            #print '--- /find() ----------------------------'
            print
            return 3
        """

        #print '--- /find() ----------------------------'
        #print ##
        return False

    def geturl(self):
        u"""
        Gmailにアクセスしメールから本文取得
        返す
        """
        urllist = []
        c = 0
        mess = u'Gmail にアクセスしています...'
        print mess
        #print ##
        while True:
            try:
                imap = IMAP4_SSL('imap.gmail.com')
                break
            except BaseException, mess:
                print str(mess)
                if c > 10:
                    import sys
                    sys.exit()
                elif c <= 10:
                    time.sleep(600)
                c += 1

        imap.login(self.gid, self.gpw)  # Gmail login
        imap.select()

        _,[data] = imap.search(None,'ALL')
        for i in data.split(' '):
            _,sub = imap.fetch(i, '(RFC822.TEXT)')
            text = sub[0][1].strip()  # メール本文すべて
            myformat = self.find(text)
            if (self.debug == False) and (myformat != False):  # 見つかって非デバッグ時
                imap.store(i, '+FLAGS', '\Deleted')  # メール削除
                imap.logout()
                return myformat
            elif (self.debug == True) and (myformat != False):  # 見つかってデバッグ時
                imap.logout()
                return myformat
            elif myformat == False:
                continue
            else:
                continue
            return False

        imap.logout()
        return False

    def checkdir(self):
        # 保存場所決定
        if os.path.exists(self.savedir):
            pass
        else:
            # savedir がなければ cdir\\movie に設定
            self.savedir = '\\movie'
        # 空きチェック
        if freespace.free_disk_space(self.savedir)[0] > 1:
            return True
        else:
            return False

    def mycheckdir(self):
        # 保存場所決定
        if os.path.exists(self.savedir):
            pass
        else:
            # savedir がなければ cdir\\movie に設定
            self.savedir = r'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\Temporary Files'
        # 空きチェック
        if freespace.free_disk_space(self.savedir)[0] > 1:
            return True
        else: return False;

# -*- coding: utf-8 -*-

import datetime
import free_disc_space as freespace
import logging
import nicodl_various as Various
import nicodl_sendmail as SendMail
import nicovideo as Nicovideo
import re
import os.path
import pickle
import sys
import threading
import time
import wx
#import youtube_search as youtube_search

from imaplib import *

u"""
code ### : 表示用
code ##  : 必要空白行
"""

# 新しいイベントクラスとイベントを定義する
EVT_TYPE_DL = wx.NewEventType()
EVT_DL = wx.PyEventBinder(EVT_TYPE_DL)


class DownloadEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid):
        wx.PyCommandEvent.__init__(self, etype, eid)

    def GetValue(self):
        return True

class RemoteNicovideoDL(threading.Thread):
    def __init__(self, parent, directory=None, debug=True):
        """
        debug = True/False
        """
        # threading
        threading.Thread.__init__(self)
        self.setDaemon(True)

        # GUI
        self.parent = parent
        #
        self.cdir = directory  # カレントディレクトリ
        self.url_front =  r'http://www.nicovideo.jp/watch/'
        self.myformats = []
        self.debug = debug
        self.empty = True  # emptyメッセージ表示フラグ
        self.message = u'NicoVideoDL'  # GUI表示用
        # display
        self.display_download = 0
        self.movie_id_display = u"動画ID"
        self.title_display = u"タイトル"
        self.description_display = u"動画説明"
        self.options = u"オプション"
        self.thumbnail_display = False

        if debug:
            self.start_wait_time = 1  # windows 起動待ち
            self.timeout_wait_time = 3  # Internet 接続失敗時
            self.wait_time = 1  # DL間隔
            self.empty_wait_time = 3  # DLリストが空の時の待ち時間
            info_file = "test\\info.ndl"
            self.backupfile = 'data\\test2_backup.txt'
            logfile = ''.join([str(datetime.date.today()), ' test.txt'])
        else:
            self.start_wait_time = 3#00  # 5分
            self.timeout_wait_time = 300  # 5分
            self.wait_time = 30#0
            self.empty_wait_time = 6#00
            info_file = "data\\info.ndl"
            self.backupfile = 'data\\backup.txt'
            logfile = ''.join([str(datetime.date.today()), '.txt'])

        # info
        f = open(info_file)
        info = pickle.load(f)
        f.close()
        self.gid = info["gmail_ID"]
        self.gpw = info["gmail_PW"]
        self.nicoid = info["nico_ID"]
        self.nicopw = info["nico_PW"]
        self.toaddr = info["to_addr"]
        self.savedir = info["savedir"]

        # logging setting
        """
        if False == os.path.exists('.\\data\\log'):
            os.mkdir('.\\data\\log')
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(filename)s:%(lineno)d] %(asctime)s %(levelname)s %(message)s',
                            filename=''.join([self.cdir, '\\data\\log\\', logfile]), # logファイル置き場
                            filemode='a')"""

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
        #print '--- find() -----------------------------'
        #print text
        matched = re.search('[sn][mo]\d+', text)  # videoID検索
        #print 'find() matched videoID: %s' % matched ###
        if matched:
            video_id = matched.group()
            print 'Hit!: %s' % video_id ###
            myformat = nicodl_various.make_myformat(movie_id=video_id, state=False)  # movie format
            #print '--- /find() ----------------------------'
            print ##
            return myformat

        matched = re.search('mylist/\d+', text)  # mylistID検索
        #print 'find() matched mylistID: %s' % matched ###
        if matched:
            mylist_id = matched.group().strip('mylist/')
            print 'Hit! mylistID: %s' % mylist_id ###
            myformat = nicodl_various.make_myformat(mylist_id=mylist_id)  # mylist format
            print 'Waiting...'
            time.sleep(0.1)
            #print '--- /find() ----------------------------'
            print ##
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
        print ##
        return False

    def geturl(self):
        u"""
        Gmailにアクセスしメールから本文取得
        返す
        """
        urllist = []
        c = 0
        mess = u'Gmail にアクセスしています.'
        print mess
        print ##
        while True:
            try:
                imap = IMAP4_SSL('imap.gmail.com')
                break
            except BaseException, mess:
                logging.error(mess)
                if c > 10:
                    import sys
                    logging.error('gmail cant be conected...')
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
                return myformat
            elif (self.debug == True) and (myformat != False):  # 見つかってデバッグ時
                return myformat
            elif myformat == False:
                continue
            else:
                continue
            return False

        imap.logout()

    def separation(self, myformat):
        """
        myformat を渡して振り分け
        (仕様変更で不要になった)
        """
        # 振り分け
        if myformat == bool:
            return False
        if myformat["format"] == "MOVIE":
            self.movie_formats.append(myformat)  # フォーマット追加
            if self.debug == False:
                imap.store(i, '+FLAGS', '\Deleted')  # メール削除
        elif myformat["format"] == "MYLIST":
            self.mylist_formats.append(myformat)
        else:
            print 'ELSE'
            return False

        return True

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

    def run(self):
        u"""
        flag: DLするか
        """

        sendmail = SendMail.nicodl_sendmail(self.gid, self.gpw, self.toaddr)  # 完了メール送信用
        various = Various.nicoDL_Various()

        message = u''  # メール本文

        """start while loop """
        while True:

            myformat = self.geturl()  # Gmailチェック
            #print "myformat:", myformat
            if myformat == False:
                print u"Gmailが空."
                time.sleep(500)
                continue
            else:
                # library_ALL.ndl に追加
                various.write_library(myformat, os.path.join(self.cdir, "data"))
                # various.UPDATE() 後で実装

            """check RSS"""
            """/check RSS"""
            """
            if self.checkdir():
                pass
            else:
                # 空き容量不足でループをリセット
                print u"空き容量不足:\n %s" % self.savedir
                time.sleep(300)
                continue
            print self.savedir, u"に保存"
            """

            """外部表示用アトリビュート作成"""
            # ライブラリファイルリフレッシュ
            various.reflesh_libraryfile(os.path.join(self.cdir, "data", "library_ALL.ndl"))
            # RSS
            various.rsscheck(os.path.join(self.cdir, "data"))

            # DL部分
            f = open(os.path.join(self.cdir, "data", "library_ALL.ndl"))
            lib = pickle.load(f)
            f.close()
            #print lib
            for item in lib:
                #print item
                #print "for"
                #"state:",item["state"]
                if item == None:
                    continue
                elif item["format"] == "MYLIST":
                    continue
                elif (item["format"] == "MOVIE") and (item["state"]==False):
                    evt = DownloadEvent(EVT_TYPE_DL, wx.ID_ANY)
                    wx.PostEvent(self.parent, evt)
                    self.display_download = True
                    if item["mylist_id"] != None:
                        mylistflag = item["mylist_name"]
                    else:
                        mylistflag = None
                    nico = Nicovideo.Nicovideo(movie_id=item["movie_id"])
                    # display
                    self.movie_id_display = item["movie_id"]  #
                    evt = DownloadEvent(EVT_TYPE_DL, wx.ID_ANY)
                    wx.PostEvent(self.parent, evt)
                    #self.options_display = item["options"]  #
                    # 情報取得
                    title = self.title_display = nico.get_movie_title()  #
                    evt = DownloadEvent(EVT_TYPE_DL, wx.ID_ANY)
                    wx.PostEvent(self.parent, evt)
                    length = nico.get_movie_length()
                    description = self.description_display = nico.get_movie_description()  #
                    evt = DownloadEvent(EVT_TYPE_DL, wx.ID_ANY)
                    wx.PostEvent(self.parent, evt)
                    print title,length
                    minute = int(length.split(':')[0])
                    second = int(length.split(':')[1])
                    now = datetime.datetime.now()
                    end = now + datetime.timedelta(minutes=minute, seconds=second)
                    end = end.strftime('%m/%d %H:%M')
                    print end, u"頃終了."
                    # DL
                    print item["movie_id"], u"サムネ取得中...",
                    thumbnail = self.thumbnail_display = nico.save_thumbnail(os.path.join(self.cdir, "data\\thumbnail"))
                    evt = DownloadEvent(EVT_TYPE_DL, wx.ID_ANY)
                    wx.PostEvent(self.parent, evt)
                    print u"完了!"
                    print self.thumbnail_display
                    print item["movie_id"], u"DL中...",
                    movie_path = nico.save_movie(self.nicoid, self.nicopw, self.savedir, mylist=mylistflag)
                    print u"完了!\n %s" % movie_path
                    # 情報書き換え
                    various.rewrite_library(key="thumbnail", value=thumbnail, libraryfilepath=os.path.join(self.cdir, "data\\library_ALL.ndl"),movie_id=item["movie_id"])
                    various.rewrite_library(key="state", value=True, libraryfilepath=os.path.join(self.cdir, "data\\library_ALL.ndl"),movie_id=item["movie_id"])
                    various.rewrite_library(key="movie_path", value=movie_path, libraryfilepath=os.path.join(self.cdir, "data\\library_ALL.ndl"),movie_id=item["movie_id"])
                    # マイリスが登録されていたらそのマイリスのDL済みに追加
                    if item["mylist_id"] != None:
                        f = open(os.path.join(self.cdir, "data", "library_ALL.ndl"))
                        my = pickle.load(f)
                        f.clise()
                        for i in my:
                            if i["mylist_id"] == item["mylist_id"]:
                                various.rewrite_library(key="downloaded", value=item["movie_id"], libraryfilepath=os.path.join(self.cdir, "data\\library_ALL.ndl"),mylist_id=item["mylist_id"])

                    # メール送信
                    mail = SendMail.nicodl_sendmail(self.gid, self.gpw, self.toaddr)
                    mail.main(description, item["movie_id"])
                    # 外部表示用アトリビュートリセット
                    self.movie_id_display = u"動画ID"
                    self.title_display = u"タイトル"
                    self.description_display = u"動画説明"
                    self.options = u"オプション"
                    self.thumbnail_display = False
                    self.display_download = 0
                    evt = DownloadEvent(EVT_TYPE_DL, wx.ID_ANY)
                    wx.PostEvent(self.parent, evt)


                    #break


            print u"Waiting..."
            time.sleep(self.wait_time)




if __name__ == '__main__':

    #ユーザー設定部
    os.chdir(r"C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\nicoDL_dev\nicoDL")
    directory = os.getcwd()

    nicodl = RemoteNicovideoDL(os.getcwd(), debug=False) # debug = bool
    nicodl.start()
    #nicodl.run()


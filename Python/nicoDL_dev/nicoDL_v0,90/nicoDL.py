#!/usr/bin/env python
#-*- coding: utf-8 -*-

#import nicodl_thread as nicodl_main
import nicodl_various as various
import os
import pickle
import sys
import threading
import wx

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
#import youtube_search as youtube_search

from imaplib import *

class RedirectText(object):
    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl

    def write(self,string):
        self.out.WriteText(string)


# 新しいイベントクラスとイベントを定義する
EVT_TYPE_DL = wx.NewEventType()
EVT_DL = wx.PyEventBinder(EVT_TYPE_DL)

class DownloadEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid):
        wx.PyCommandEvent.__init__(self, etype, eid)

    def GetValue(self):
        return True
u"""
code ### : 表示用
code ##  : 必要空白行
"""
class RemoteNicovideoDL(threading.Thread):
    def __init__(self, parent, directory=None, debug=False):
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
            self.start_wait_time = 300  # 5分
            self.timeout_wait_time = 300  # 5分
            self.wait_time = 300
            self.empty_wait_time = 600
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
            #print ##
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
            if myformat == False:  # Gamilが空
                pass
            else:
                # library_ALL.ndl に追加
                various.write_library(myformat, os.path.join(self.cdir, "data"))
                # various.UPDATE() 後で実装

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
                    wx.PostEvent(self.parent, evt)
                    #self.options_display = item["options"]  #
                    # 情報取得
                    title = self.title_display = nico.get_movie_title()  #
                    wx.PostEvent(self.parent, evt)
                    length = nico.get_movie_length()
                    description = self.description_display = nico.get_movie_description()  #
                    wx.PostEvent(self.parent, evt)
                    print "".join(["[",item["movie_id"], "]",title, length])
                    minute = int(length.split(':')[0])
                    second = int(length.split(':')[1])
                    now = datetime.datetime.now()
                    end = now + datetime.timedelta(minutes=minute, seconds=second)
                    end = end.strftime('%m/%d %H:%M')
                    print "".join(["[",item["movie_id"], "]",end, u"頃終了します."])
                    # DL
                    print "".join(["[",item["movie_id"], "]",u" サムネイル取得中..."])
                    thumbnail = self.thumbnail_display = nico.save_thumbnail(os.path.join(self.cdir, "data\\thumbnail"))
                    wx.PostEvent(self.parent, evt)
                    print "".join(["[",item["movie_id"], "]",u" サムネイル取得完了!"])
                    print "".join(["[",item["movie_id"], "]",u" 動画取得中..."])
                    movie_path = nico.save_movie(self.nicoid, self.nicopw, self.savedir, mylist=mylistflag)
                    print "".join(["[",item["movie_id"], "]",u" 動画取得完了!", "\n", movie_path])
                    # 情報書き換え
                    print "".join(["[",item["movie_id"], "]",u" 情報を更新します..."])
                    various.rewrite_library(key="thumbnail", value=thumbnail, libraryfilepath=os.path.join(self.cdir, "data\\library_ALL.ndl"),movie_id=item["movie_id"])
                    various.rewrite_library(key="state", value=True, libraryfilepath=os.path.join(self.cdir, "data\\library_ALL.ndl"),movie_id=item["movie_id"])
                    various.rewrite_library(key="movie_path", value=movie_path, libraryfilepath=os.path.join(self.cdir, "data\\library_ALL.ndl"),movie_id=item["movie_id"])
                    # マイリスが登録されていたらそのマイリスのDL済みに追加
                    if item["mylist_id"] != None:
                        f = open(os.path.join(self.cdir, "data", "library_ALL.ndl"))
                        my = pickle.load(f)
                        f.close()
                        for i in my:
                            if i["mylist_id"] == item["mylist_id"]:
                                various.rewrite_library(key="downloaded", value=item["movie_id"], libraryfilepath=os.path.join(self.cdir, "data\\library_ALL.ndl"),mylist_id=item["mylist_id"])

                    # メール送信
                    print "".join(["[",item["movie_id"], "]",u" 完了メール送信"])
                    mail = SendMail.nicodl_sendmail(self.gid, self.gpw, self.toaddr)
                    mail.main(description, item["movie_id"])
                    # 外部表示用アトリビュートリセット
                    self.movie_id_display = u"動画ID"
                    self.title_display = u"タイトル"
                    self.description_display = u"動画説明"
                    self.options = u"オプション"
                    self.thumbnail_display = False
                    self.display_download = 0
                    wx.PostEvent(self.parent, evt)
                    #break
            print "".join([u"待機中..."])
            time.sleep(self.wait_time)


class MyURLDropTarget(wx.PyDropTarget):
    def __init__(self, window):
        wx.PyDropTarget.__init__(self)
        self.window = window

        self.data = wx.URLDataObject();
        self.SetDataObject(self.data)

    def OnDragOver(self, x, y, d):
        return wx.DragLink

    def OnData(self, x, y, d):
        if not self.GetData():
            return wx.DragNone

        url = self.data.GetURL()
        self.window.AppendText(url + "\n")

        return d


class nicoDL_mainWindow(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.url =u""

        self.mess = u"nicoDL"
        self.title = u'タイトル'
        self.empty = u"Option"
        self.description = u"動画説明"
        self.movie_id = u"sm99999999"
        self.thumbnailfile = r"\\data\\default.jpeg"
        self.bar = u"プログレスバー"

        # サムネ
        bmp = wx.EmptyBitmap(130,100)
        self.thumbnail = wx.StaticBitmap(self, -1, bmp)

        # Wigets
        #self.mess_st = wx.StaticText(self, -1, self.mess)
        self.title_st = wx.StaticText(self, -1, self.title)
        self.option_st = wx.StaticText(self, -1, self.empty)
        self.description_tc = wx.TextCtrl(self, -1, self.description,size=(150, 100), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.movie_id_st = wx.StaticText(self, -1, self.movie_id)
        #self.bar_st = wx.StaticText(self, -1, self.bar)
        if not hasattr(self, "url_id"):
            self.url_id = wx.NewId()
        self.url_tc = wx.TextCtrl(self, id=self.url_id, value=u"",style=wx.TE_MULTILINE, size=(300,37))
        # Button
        url_btn = wx.Button(self, -1, 'DL', size=(50,37))
        # log
        self.log_tc = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)

        # Sizer
        sizer = wx.GridBagSizer(9,4)  # 大元
        sizer0 = wx.BoxSizer(wx.VERTICAL)
        # Add sizer
        #sizer.Add(self.mess_st, (0,0))
        sizer0.Add(self.title_st, 1, flag=wx.EXPAND)
        sizer.Add(self.thumbnail,(0,0), (3,1))
        sizer0.Add(self.description_tc, 1, flag=wx.EXPAND)
        sizer.Add(self.movie_id_st,(0,1))
        sizer.Add(self.option_st,(1,1))
        sizer.Add(self.url_tc, (3,0), (3,2))
        sizer.Add(url_btn, (3,2))
        #sizer.Add(self.bar_st,(6,3))#, (6,2),flag=wx.EXPAND)
        sizer.Add(self.log_tc,(0,3), (5,5),flag=wx.EXPAND)
        sizer.AddGrowableCol(4)
        sizer0.Add(sizer, 1, flag=wx.EXPAND)
        self.SetSizerAndFit(sizer0)

        # Bind
        self.Bind(wx.EVT_TEXT, self.OnGetText, id=self.url_id)
        self.Bind(wx.EVT_BUTTON, self.OnGetURL)

        # URL D&D
        self.url_tc.SetDropTarget(MyURLDropTarget(self.url_tc))

        # redirect text here
        redir=RedirectText(self.log_tc)
        sys.stdout=redir

    def redisplay(self):
        """動画情報再表示"""
        #print "redisplay"
        #self.mess_st.SetLabel(self.mess)
        #print self.title
        self.title_st.SetLabel(self.title)
        self.option_st.SetLabel(u"オプション未実装")
        self.description_tc.SetValue(self.description)
        self.movie_id_st.SetLabel(self.movie_id)
        if self.thumbnailfile == False: # サムネ
            self.thumbnailfile = r"data\\default.jpeg"
        bmp = wx.Bitmap(self.thumbnailfile, wx.wx.BITMAP_TYPE_JPEG)
        self.thumbnail.SetBitmap(bmp)

    def OnGetURL(self, evt):
        """受け取った値をlibraryに書き込む"""
        nico = RemoteNicovideoDL(None)
        myformat = nico.find(self.url)
        #print myformat
        if myformat:
            vari = various.nicoDL_Various()
            vari.write_library(myformat, os.path.join(os.getcwd(), "data"))
        else:
            pass
        self.url = ""
        self.url_tc.SetValue("")

    def OnGetText(self, evt):
        """TCの値を受け取る"""
        tc = evt.GetEventObject()
        self.url = tc.GetValue()
        #print self.url


class nicoDL_mylistWindow(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, u"This is a mylist object\n工事中", (20,20))


class nicoDL_setupWindow(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.load()  # 初期値決定

        # text
        gmail_ID_t = wx.StaticText(self, -1, "Gmail ID")
        gmail_PW_t = wx.StaticText(self, -1, "Gmail PW")
        nico_ID_t = wx.StaticText(self, -1, u"ニコニコ動画ID")
        nico_PW_t = wx.StaticText(self, -1, u"ニコニコ動画PW")
        to_addr_t = wx.StaticText(self, -1, u"完了メール送信先アドレス")
        savedir_t = wx.StaticText(self, -1, u"動画保存フォルダ")

        # Save Button
        save_button = wx.Button(self, -1, label=u'保存')

        # Choose Directory
        savedir_button = wx.Button(self, -1, label=u"フォルダを選択")

        # TextControls
        gmail_ID_tc = wx.TextCtrl(self, -1, value=self.gmail_ID_pre)
        gmail_PW_tc = wx.TextCtrl(self, -1, value=self.gmail_PW_pre, style=wx.TE_PASSWORD)
        nico_ID_tc = wx.TextCtrl(self, -1, value=self.nico_ID_pre)
        nico_PW_tc = wx.TextCtrl(self, -1, value=self.nico_PW_pre, style=wx.TE_PASSWORD)
        to_addr_tc = wx.TextCtrl(self, -1, value=self.to_addr_pre)
        self.savedir_tc = wx.TextCtrl(self, -1, value=self.savedir_pre, style=wx.TE_READONLY)

        # Bind
        self.Bind(wx.EVT_TEXT, self.TextControl_Gmail_ID, gmail_ID_tc)
        self.Bind(wx.EVT_TEXT, self.TextControl_Gmail_PW, gmail_PW_tc)
        self.Bind(wx.EVT_TEXT, self.TextControl_Nico_ID, nico_ID_tc)
        self.Bind(wx.EVT_TEXT, self.TextControl_Nico_PW, nico_PW_tc)
        self.Bind(wx.EVT_TEXT, self.TextControl_To_Addr, to_addr_tc)
        self.Bind(wx.EVT_BUTTON, self.Button_Savedir_Evt, savedir_button)
        self.Bind(wx.EVT_BUTTON, self.save, save_button)

        # panel
        dummy_panel_1 = wx.Panel(self, -1)
        dummy_panel_2 = wx.Panel(self, -1)
        dummy_panel_3 = wx.Panel(self, -1)
        dummy_panel_4 = wx.Panel(self, -1)
        dummy_panel_5 = wx.Panel(self, -1)
        dummy_panel_6 = wx.Panel(self, -1)
        dummy_panel_7 = wx.Panel(self, -1)

        # sizer
        layout = wx.GridSizer(7,3)
        layout.Add(gmail_ID_t, flag=wx.ALIGN_CENTRE)
        layout.Add(gmail_ID_tc, flag=wx.ALIGN_CENTRE)
        layout.Add(dummy_panel_1)
        layout.Add(gmail_PW_t, flag=wx.ALIGN_CENTRE)
        layout.Add(gmail_PW_tc, flag=wx.ALIGN_CENTRE)
        layout.Add(dummy_panel_2)
        layout.Add(nico_ID_t, flag=wx.ALIGN_CENTRE)
        layout.Add(nico_ID_tc, flag=wx.ALIGN_CENTRE)
        layout.Add(dummy_panel_3)
        layout.Add(nico_PW_t, flag=wx.ALIGN_CENTRE)
        layout.Add(nico_PW_tc, flag=wx.ALIGN_CENTRE)
        layout.Add(dummy_panel_4)
        layout.Add(to_addr_t, flag=wx.ALIGN_CENTRE)
        layout.Add(to_addr_tc, flag=wx.ALIGN_CENTRE)
        layout.Add(dummy_panel_5)
        layout.Add(savedir_t, flag=wx.ALIGN_CENTRE)
        layout.Add(self.savedir_tc, flag=wx.ALIGN_CENTRE)
        layout.Add(savedir_button, flag=wx.ALIGN_CENTRE)
        layout.Add(dummy_panel_6)
        layout.Add(dummy_panel_7)
        layout.Add(save_button, flag=wx.ALIGN_RIGHT)
        self.SetSizer(layout)


    def load(self):
        """
        データの読み込み
        """
        try:
            f = open("data\\info.ndl")
            info = pickle.load(f)
            f.close()
            self.gmail_ID = self.gmail_ID_pre = info["gmail_ID"]
            self.gmail_PW = self.gmail_PW_pre = info["gmail_PW"]
            self.nico_ID = self.nico_ID_pre = info["nico_ID"]
            self.nico_PW = self.nico_PW_pre = info["nico_PW"]
            self.to_addr = self.to_addr_pre = info["to_addr"]
            self.savedir = self.savedir_pre = info["savedir"]
        except IOError:
            print u"info 初期化"
            self.gmail_ID = self.gmail_ID_pre = u""
            self.gmail_PW = self.gmail_PW_pre = u""
            self.nico_ID = self.nico_ID_pre = u""
            self.nico_PW = self.nico_PW_pre = u""
            self.to_addr = self.to_addr_pre = u""
            self.savedir = self.savedir_pre = u""

    def save(self, evt):
        """
        データの保存
        """
        self.gmail_ID = self.gmail_ID_pre
        self.gmail_PW = self.gmail_PW_pre
        self.nico_ID = self.nico_ID_pre
        self.nico_PW = self.nico_PW_pre
        self.to_addr = self.to_addr_pre
        self.savedir = self.savedir_pre

        info = {
                "gmail_ID":self.gmail_ID,
                "gmail_PW":self.gmail_PW,
                "nico_ID":self.nico_ID,
                "nico_PW":self.nico_PW,
                "to_addr":self.to_addr,
                "savedir":self.savedir,
                }
        #print info
        print u"ユーザー情報を保存."
        try:
            f = open("data\\info.ndl", "w")
            pickle.dump(info, f)
        finally:
            f.close()

    def Button_Savedir_Evt(self, evt):
        """
        フォルダ取得
        """
        self.savedir_tc.SetValue(u"")
        savedir_dd = wx.DirDialog(self, defaultPath=self.savedir_pre)
        if savedir_dd.ShowModal() == wx.ID_OK:
            self.savedir_pre = savedir_dd.GetPath()
        savedir_dd.Destroy()
        self.savedir_tc.WriteText(self.savedir_pre)
        #print self.savedir_pre

    def TextControl_Gmail_ID(self, evt):
        """
        Gmail ID 取得
        """
        tc = evt.GetEventObject()
        self.gmail_ID_pre = tc.GetValue()
        #print self.gmail_ID_pre

    def TextControl_Gmail_PW(self, evt):
        """
        Gmail PW 取得
        """
        tc = evt.GetEventObject()
        self.gmail_PW_pre = tc.GetValue()
        #print self.gmail_PW_pre

    def TextControl_Nico_ID(self, evt):
        """
        ニコニコ動画 ID 取得
        """
        tc = evt.GetEventObject()
        self.nico_ID_pre = tc.GetValue()
        #print self.nico_ID_pre

    def TextControl_Nico_PW(self, evt):
        """
        ニコニコ動画 PW 取得
        """
        tc = evt.GetEventObject()
        self.nico_PW_pre = tc.GetValue()
        #print self.nico_PW_pre

    def TextControl_To_Addr(self, evt):
        """
        通知メール送信先 取得
        """
        tc = evt.GetEventObject()
        self.to_addr_pre = tc.GetValue()
        #print self.to_addr_pre

class nicoDL(wx.Frame):
    def __init__(self, size=wx.DefaultSize, pos=wx.DefaultPosition, *args, **kwds):
        wx.Frame.__init__(self, None, title="nicoDL",
                          pos = pos,
                          size = size,
                          style=wx.MAXIMIZE_BOX |
                                wx.RESIZE_BORDER |
                                wx.SYSTEM_MENU |
                                wx.CAPTION |
                                wx.CLOSE_BOX |
                                wx.CLIP_CHILDREN)
        self.display_flag = 0

        # ICON
        self.tb_ico = wx.TaskBarIcon()
        self.ico = wx.Icon("data\\nicodl.ico", wx.BITMAP_TYPE_ICO)
        self.tb_ico.SetIcon(self.ico, u"nicoDL is runnnig!!")

        #create Panel and a notebook on the panel
        panel = wx.Panel(self)
        notebook = wx.Notebook(panel)
        # create the page windows
        self.win_main = nicoDL_mainWindow(notebook)
        win_mylist = nicoDL_mylistWindow(notebook)
        win_setup = nicoDL_setupWindow(notebook)
        # add the pages
        notebook.AddPage(self.win_main, u'メイン')
        notebook.AddPage(win_mylist, 'win_mylist')
        notebook.AddPage(win_setup, u'設定')
        # put the notebook in a sizer for the panel to manage the layout
        sizer = wx.BoxSizer()
        sizer.Add(notebook, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        # Bind
        self.tb_ico.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.OnRightUp)
        self.Bind(EVT_DL, self.display_reserve)
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.Show()  ## 起動時に表示するか

        # main
        print u"nicoDL 開始"
        if self.loadtest():
            self.main = RemoteNicovideoDL(self, os.getcwd(), debug=False)
            try:
                self.main.start()
            except:
                print u"エラーが発生しました.\n1度終了してください."

    #
    def display_reserve(self, evt):
        """
        値変更
        """
        #print "display_reserve"
        try:
            self.win_main.title = self.main.title_display
            self.win_main.movie_id = self.main.movie_id_display
            self.win_main.description = self.main.description_display
            self.win_main.thumbnailfile = self.main.thumbnail_display
            self.win_main.redisplay()
        except AttributeError:
            pass

    def loadtest(self):
        """
        データの読み込みテスト
        """
        try:
            f = open("data\info.ndl")
            info = pickle.load(f)
            f.close()
            self.gmail_ID  = info["gmail_ID"]
            self.gmail_PW  = info["gmail_PW"]
            self.nico_ID  = info["nico_ID"]
            self.nico_PW  = info["nico_PW"]
            self.to_addr  = info["to_addr"]
            self.savedir  = info["savedir"]
            return True

        except BaseException:
            return False
            print u"info 初期化"


    # Taskbar
    def OnRightUp(self, event):
        if not hasattr(self, "popupID1"):  # 起動後、一度だけ定義する。
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            self.tb_ico.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1) # Bind 先が icon なのがミソ
            self.tb_ico.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
        # メニュー作成
        menu = wx.Menu()
        menu.Append(self.popupID1, u"ウィンドウを表示")
        menu.AppendSeparator()
        menu.Append(self.popupID2, u"終了")

        self.tb_ico.PopupMenu(menu)
        menu.Destroy()

    def OnPopupOne(self, evt):
        #print 'OnPopupOne'
        self.Show()

    def OnPopupTwo(self, evt):
        #print 'OnPopupTwo'
        self.OnExitApp(None)
    # Taskbar ココまで

    def OnMove(self, evt):
        """位置取得"""
        self.mypos = evt.GetPosition()

    def OnSize(self, evt):
        """サイズ取得"""
        self.mysize= evt.GetSize()
        evt.Skip()

    def OnClose(self, evt):
        """
        バツ押したとき
        """
        #print "CloseEvent"
        self.Hide()

    def OnExitApp(self, evt):
        """
        終了処理
        """
        f = open("data\\info.ndl")
        info = pickle.load(f)
        f.close()
        info["window_pos"] = (self.mypos.x, self.mypos.y)
        info["window_size"] = (self.mysize.width, self.mysize.height)
        f = open("data\\info.ndl", "w")
        pickle.dump(info, f)
        f.close()

        self.tb_ico.Destroy()
        self.Destroy()


if __name__ == '__main__':
    try:
        f = open("data\\info.ndl")
        info = pickle.load(f)
        f.close()
        pos = info["window_pos"]
        size = info["window_size"]
        print pos, size
        app = wx.App()
        nicodl = nicoDL(pos=pos, size=size)
        app.MainLoop()
    except:
        app = wx.App()
        nicodl = nicoDL()
        app.MainLoop()





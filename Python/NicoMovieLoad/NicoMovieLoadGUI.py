#!/usr/bin/env python
# -*- coding: utf-8 -*-
# generated by wxGlade 0.6.4 on Thu Feb 28 14:01:44 2013

import images
import os
import platform
import sys
import threading
import time
import wx
import wx.gizmos as gizmos
from modules.nicoLoad_base import Log
from modules.nicoLoad_database import Database
from modules.nicoLoad_database import SystemDatabase
from modules.nicoLoad_various import nicoLoad_Various as NVarious
from modules.nicoLoad_saveMovi1 import NicoLoad_SaveMovie as SaveMovie
from modules.nicoLoad_table import NicoLoad_table as NTable
from modules.nicoLoad_queue import nicoLoad_queue as NQueue
from modules.nicovideoAPI import NicovideoAPI

# begin wxGlade: extracode
# end wxGlade

WORKDIR = ur".NML"
DATABASE_FILE = u"nml.db"
SYSTEM_DATABASE_FILE = u"nml_sys.db"

class NicoMovieLoadMain():
    def __init__(self, databasePath, systemDatabasePath, logging):
        """
        databasePath: database file path
        systemDatabasePath: system database file path
        logging: log function
        """
        self.databasePath = databasePath
        self.systemDatabasePath = systemDatabasePath
        #self.logging = logging

        self._wtime_load = 60 * 60 * 12  # wait times
        self._wtime_scan = 60 * 60 * 12
        self._wtime_rss = 60 * 60 * 12
        self.__flag_mainLoop = True  # mainLoop
        self.__flag_loading = False  # load
        self.__flag_scanning = False  # scan
        self.__flag_rssing = False  # rss
        self.sysenc = sys.getfilesystemencoding()

        self.queue = NQueue()
        self.saveMovie = SaveMovie(1024)

    def logging(self, text):
        print text

    def main(self):
        """
        call each daemons
        """
        db = Database(self.databasePath)
        db.ctTable()
        db.close()

        daemon = (self.daemonRss,
                  self.daemonScan,
                  self.daemonLoad,
                  )
        for func in daemon:
            th = threading.Thread(target=func)
            th.daemon = True
            th.start()
            time.sleep(3)

    def load(self, movieid):
        """
        load movieid
        """
        movieid = movieid
        self.logging("load: %s" % movieid)
        # 各データの取得
        db = Database(self.databasePath)
        sdb = SystemDatabase(self.systemDatabasePath)
        nicoid = sdb.getNicoid()
        nicopw = sdb.getNicopw()
        savedir = sdb.getSavedir()
        sdb.close()
        api = NicovideoAPI(movie_id=movieid)
        title = api.get_movie_title()
        moviePath = api.save_movie(nicoid, nicopw, savedir)  # 保存専用のクラスを定義する。一時停止可能なもの
        # 登録
        db.setMoviePath(movieid, moviePath)
        db.setMovieState(movieid, 1)
        self.queue.done()
        db.close()
        return True

    def cancel(self):
        self.saveMovie.cancel()


    def find(self, text):
        """
        find movieid/mylistid from text
        """
        various = NVarious(None, self.logging)
        return various.find(text)

    def _scanning(self):
        """
        scanning the database
        add to queue videos id unloaded
        should be called at regular intervals

        retunrn: added movieid num in queue
        """
        num = 0
        self.logging("scanning")
        db = Database(self.databasePath)
        for movieid in db.getMovieState0():
            self.queue.add(movieid)
            self.logging("AddQueue: %s" % movieid)
            num += 1
        db.close()
        return num

    def _rss(self):
        """
        check new movieid from include mylistid
        register in database to the new movieid
        """
        self.logging("rss")
        db = Database(self.databasePath)
        for mylistid in db.getMylistAll():
            if db.getMylistRss(mylistid):
                self.logging("RSS: %s" % mylistid)
                hitNum = 0
                apiMylist = NicovideoAPI.Nicovideo(mylistid=mylistid)
                for movieid in apiMylist.get_mylist_movies():
                    if not(movieid in db.getMylistHasMovieFromMylistId(mylistid)):
                        self.logging("RSS: Hit: %s" % movieTitle)
                        db.addMylistHasMovie(mylistid, movieid)
                        self.register(movieid)
                        db.setMovieTitle(movieid, movieTitle)
                        hitNum += 1
                self.logging("RSS: %s: %2dhit" % (mylistid, hitNum))
        db.close()

    def register(self, mid):
        """
        register in database mid
        if mid is already registered, it marks unload

        mid: mylistid or movieid
        return: bool
        """
        db = Database(self.databasePath)
        if mid[0:2] == "sm":
            if db.extMovieidInTable(mid):
                db.setMovieState(mid, 0)
            else:
                apiMovie = NicovideoAPI(movie_id=mid)
                movieTitle = apiMovie.get_movie_title()
                db.addMovie(mid)
                db.setMovieTitle(mid, movieTitle)
        else:
            if db.extMylistInTable(mid):
                db.setMylistRss(mid, 1)
            else:
                api = NicovideoAPI(mylist_id=mid)
                mylistTitle = api.get_mylist_title().decode(self.sysenc)
                db.addMylist(mid)
                db.setMylistTitle(mylistTitle)
        db.close()

    def daemonLoad(self):
        """
        daemon with self.load

        interval: interval function is called
        """
        """
        一定時間(interval)ごとにself.load()を呼ぶ
        重複呼び出しをしないようにフラグ管理
        このフラグはself.doneで戻す
        """
        while True:
            self.logging("daemon load")
            if self.__flag_loading == False:
                if not self.queue.empty():
                    self.__flag_loading = True
                    mid = self.queue.get()
                    print "mid:", mid
                    self.load(mid)
                    #self.load(self.queue.get())
                    self.queue.done()
                else:
                    for i in xrange(self._wtime_load):
                        time.sleep(1)
                        # 中断処理 #

    def daemonScan(self):
        """
        daemon with self.scanning

        interval: interval function is called
        """
        while True:
            self.logging("daemon scan")
            if self.__flag_scanning == False:
                self.__flag_scanning = True
                self._scanning()
            for i in xrange(self._wtime_scan):
                time.sleep(1)
                # 中断処理 #

    def daemonRss(self):
        """
        daemon with self.rss
        
        interval: interval function is called
        """
        while True:
            self.logging("daemon rss")
            if self.__flag_rssing == False:
                self.__flag_rssing = True
                self._rss()
            for i in xrange(self._wtime_rss):
                time.sleep(1)
                # 中断処理 #

    # flag setter
    #def setFlagMain(self, flag):
    #    self.__flag_ing = flag
    def setFlagLoad(self, flag):
        self.__flag_loading = flag
    def setFlagScan(self, flag):
        self.__flag_scanning = flag
    def setFlagRss(self, flag):
        self.__flag_rssing = flag
    # flag getter
    def getFlagLoad(self):
        self.__flag_loading
    def getFlagScan(self):
        self.__flag_scaning
    def getFlagRss(self):
        self.__flag_rssing
    # wait time setter
    def setWtimeLoad(self, interval):
        self._wtime_load = interval
    def setWtimeScan(self, interval):
        self._wtime_scan = interval
    def setWtimeRss(self, interval):
        self._wtime_rss = interval
    # wait time getter
    def getWtimeLoad(self):
        return self._wtime_load
    def getWtimeScan(self):
        return self._wtime_scan
    def getWtimeRss(self):
        return self._wtime_rss

    def getQueueObj(self):
        return self.queue

class SettingsDialog(wx.Dialog):
    def __init__(self, nicoTable, logging,  *args, **kwds):
        self.nicoTable = nicoTable
        self.logging = logging
        self.nicoid = self.nicoTable.getNicoid()
        self.nicopw = self.nicoTable.getNicopw()
        self.gmailid = self.nicoTable.getGmailid()
        self.gmailpw = self.nicoTable.getGmailpw()
        self.savedir = self.nicoTable.getSavedir()

        # begin wxGlade: SettingsDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP
        wx.Dialog.__init__(self, *args, **kwds)
        self.pnlNicoid = wx.Panel(self, -1)
        self.lblNicoid = wx.StaticText(self.pnlNicoid, -1, "ID:")
        self.tclNicoid = wx.TextCtrl(self.pnlNicoid, -1, self.nicoid)
        self.btnNicoid = wx.Button(self.pnlNicoid, -1, "OK")
        self.pnlNicopw = wx.Panel(self, -1)
        self.lblNicopw = wx.StaticText(self.pnlNicopw, -1, "PW:")
        self.tclNicopw = wx.TextCtrl(self.pnlNicopw, -1, self.nicopw, style=wx.TE_PASSWORD)
        self.btnNicopw = wx.Button(self.pnlNicopw, -1, "OK")
        self.szrNico = wx.StaticBox(self, -1, u"ニコニコ動画")
        self.pnlGmailid = wx.Panel(self, -1)
        self.lblGmailid = wx.StaticText(self.pnlGmailid, -1, "ID:")
        self.tclGmailid = wx.TextCtrl(self.pnlGmailid, -1, self.gmailid)
        self.btnGmailid = wx.Button(self.pnlGmailid, -1, "OK")
        self.pnlGmailpw = wx.Panel(self, -1)
        self.lblGmailpw = wx.StaticText(self.pnlGmailpw, -1, "PW:")
        self.tclGmailpw = wx.TextCtrl(self.pnlGmailpw, -1, self.gmailpw, style=wx.TE_PASSWORD)
        self.btnGmailpw = wx.Button(self.pnlGmailpw, -1, "OK")
        self.szrGmail = wx.StaticBox(self, -1, "Gmail")
        self.tclSavedir = wx.TextCtrl(self, -1, self.savedir, style=wx.TE_READONLY)
        self.btnSavedirSelect = wx.Button(self, -1, u"選択")
        self.btnSavedir = wx.Button(self, -1, "OK")
        self.szrSavedir = wx.StaticBox(self, -1, u"保存ディレクトリ")
        self.sln = wx.StaticLine(self, -1)
        self.btnClose = wx.Button(self, -1, u"閉じる")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        self.__bind()

    def __bind(self):
        self.Bind(wx.EVT_BUTTON, self.registerNicoid, self.btnNicoid)
        self.Bind(wx.EVT_BUTTON, self.registerNicopw, self.btnNicopw)
        self.Bind(wx.EVT_BUTTON, self.registerGmailid, self.btnGmailid)
        self.Bind(wx.EVT_BUTTON, self.registerGmailpw, self.btnGmailpw)
        self.Bind(wx.EVT_BUTTON, self.registerSavedir, self.btnSavedir)
        self.Bind(wx.EVT_BUTTON, self.registerSavedir, self.btnSavedir)
        self.Bind(wx.EVT_BUTTON, self.savedirSelect, self.btnSavedirSelect)
        self.Bind(wx.EVT_BUTTON, self.OnCloseBtn, self.btnClose)

    def savedirSelect(self, evt):
        dlg = wx.DirDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.tclSavedir.SetValue(dlg.GetPath())
        dlg.Destroy()

    def registerNicoid(self, evt):
        self.logging("register")
        self.nicoTable.watch()
        self.nicoid = self.tclNicoid.GetValue()
    def registerNicopw(self, evt):
        self.logging("register")
        self.nicopw = self.tclNicopw.GetValue()
    def registerGmailid(self, evt):
        self.logging("register")
        self.gmailid = self.tclGmailid.GetValue()
    def registerGmailpw(self, evt):
        self.logging("register")
        self.gmailpw = self.tclGmailpw.GetValue()
    def registerSavedir(self, evt):
        self.logging("register")
        self.savedir = self.tclSavedir.GetValue()

    def OnCloseBtn(self, evt):
        self.logging("OnCloseBtn")
        self.recordData()
        self.Destroy()

    def recordData(self):
        self.nicoTable.setNicoid(self.nicoid)
        self.nicoTable.setNicopw(self.nicopw)
        self.nicoTable.setGmailid(self.gmailid)
        self.nicoTable.setGmailpw(self.gmailpw)
        self.nicoTable.setSavedir(self.savedir)
        self.logging("recordData")

    def __set_properties(self):
        # begin wxGlade: SettingsDialog.__set_properties
        self.SetTitle(u"NicoMovieLoad-設定")
        self.SetSize((470, 291))
        self.btnClose.SetFocus()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: SettingsDialog.__do_layout
        szr0 = wx.BoxSizer(wx.VERTICAL)
        self.szrSavedir.Lower()
        szrSavedir = wx.StaticBoxSizer(self.szrSavedir, wx.HORIZONTAL)
        self.szrGmail.Lower()
        szrGmail = wx.StaticBoxSizer(self.szrGmail, wx.VERTICAL)
        szrGmailpw = wx.BoxSizer(wx.HORIZONTAL)
        szrGmailid = wx.BoxSizer(wx.HORIZONTAL)
        self.szrNico.Lower()
        szrNico = wx.StaticBoxSizer(self.szrNico, wx.VERTICAL)
        szrNicopw = wx.BoxSizer(wx.HORIZONTAL)
        szrNicoid = wx.BoxSizer(wx.HORIZONTAL)
        szrNicoid.Add(self.lblNicoid, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        szrNicoid.Add(self.tclNicoid, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        szrNicoid.Add(self.btnNicoid, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.pnlNicoid.SetSizer(szrNicoid)
        szrNico.Add(self.pnlNicoid, 1, wx.EXPAND, 0)
        szrNicopw.Add(self.lblNicopw, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        szrNicopw.Add(self.tclNicopw, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        szrNicopw.Add(self.btnNicopw, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.pnlNicopw.SetSizer(szrNicopw)
        szrNico.Add(self.pnlNicopw, 1, wx.EXPAND, 0)
        szr0.Add(szrNico, 1, wx.EXPAND, 0)
        szrGmailid.Add(self.lblGmailid, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        szrGmailid.Add(self.tclGmailid, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        szrGmailid.Add(self.btnGmailid, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.pnlGmailid.SetSizer(szrGmailid)
        szrGmail.Add(self.pnlGmailid, 1, wx.EXPAND, 0)
        szrGmailpw.Add(self.lblGmailpw, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        szrGmailpw.Add(self.tclGmailpw, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        szrGmailpw.Add(self.btnGmailpw, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.pnlGmailpw.SetSizer(szrGmailpw)
        szrGmail.Add(self.pnlGmailpw, 1, wx.EXPAND, 0)
        szr0.Add(szrGmail, 1, wx.EXPAND, 0)
        szrSavedir.Add(self.tclSavedir, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        szrSavedir.Add(self.btnSavedirSelect, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        szrSavedir.Add(self.btnSavedir, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        szr0.Add(szrSavedir, 1, wx.EXPAND, 0)
        szr0.Add(self.sln, 0, wx.EXPAND, 0)
        szr0.Add(self.btnClose, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(szr0)
        self.Layout()
        # end wxGlade

# end of class SettingsDialog

class NicoMovieLoadGUI(wx.Frame, Log):
    def __init__(self, *args, **kwds):
        Log.__init__(self)
        self.__queueList = []
        self.__queueDict = {}
        if platform.system().lower() == "windows":
            # win用に書く
            pass
        else:
            home = os.getenv("HOME")
        nmlHome = os.path.join(home, WORKDIR)
        if not os.path.exists(nmlHome):
            os.mkdir(nmlHome)
        self.databasePath = os.path.join(nmlHome, DATABASE_FILE)
        self.systemDatabasePath = os.path.join(nmlHome, SYSTEM_DATABASE_FILE)

        db = Database(self.databasePath)
        db.ctTable()
        db.close()
        sdb = SystemDatabase(self.systemDatabasePath)
        sdb.ctTable()
        nid = sdb.getNicoid() if sdb.getNicoid() else u""
        npw = sdb.getNicopw() if sdb.getNicopw() else u""
        gid = sdb.getGmailid() if sdb.getGmailid() else u""
        gpw = sdb.getGmailpw() if sdb.getGmailpw() else u""
        sdr = sdb.getSavedir() if sdb.getSavedir() else u""
        sdb.close()

        self.nicoTable = NTable(nid, npw, gid, gpw, sdr)

        # begin wxGlade: NicoMovieLoadGUI.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.treeCtrl = gizmos.TreeListCtrl(self, -1, style=wx.TR_HAS_BUTTONS | wx.TR_NO_LINES | wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_HIDE_ROOT | wx.TR_DEFAULT_STYLE)
        self.pnlCenter = wx.Panel(self, -1)
        self.lblUrl = wx.StaticText(self.pnlCenter, -1, "URL:")
        self.tclUrl = wx.TextCtrl(self.pnlCenter, -1, "", style=wx.TE_PROCESS_ENTER)
        self.pnlBottom = wx.Panel(self, -1)
        self.lblQueueList = wx.StaticText(self.pnlBottom, -1, "QueueList:")
        self.lclQueueList = wx.ListCtrl(self.pnlBottom, -1, style=wx.LC_REPORT | wx.LC_AUTOARRANGE | wx.LC_NO_HEADER | wx.SUNKEN_BORDER)
        self.lblLog = wx.StaticText(self.pnlBottom, -1, "Log:")
        self.tclLog = wx.TextCtrl(self.pnlBottom, -1, "", style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.static_line_1 = wx.StaticLine(self, -1, style=wx.LI_VERTICAL)
        self.pnlRight = wx.Panel(self, -1)
        self.btnRss = wx.ToggleButton(self.pnlRight, -1, "RSS")
        self.btnAdd = wx.Button(self.pnlRight, -1, u"新規登録")
        self.btnLoad = wx.Button(self.pnlRight, -1, u"再ロード")
        self.btnClearLog = wx.Button(self.pnlRight, -1, u"ログ消去")
        self.btnDelete = wx.Button(self.pnlRight, -1, u"削除")
        self.btnSettings = wx.Button(self.pnlRight, -1, u"設定")
        self.btnExit = wx.Button(self.pnlRight, -1, "Exit")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        self.__bind()
        self.__setTreeListCtrl()
        self.__set_QueueListCtrl()
        # other wigets
        self.dlgSettings = SettingsDialog(self.nicoTable, self.logging, self)
        # main
        self.nicoMain = NicoMovieLoadMain(self.databasePath, self.systemDatabasePath, self.logging)
        self.nicoMain.main()
        # timer
        timer = wx.Timer(self)
        timer.Start(3 * 1000)
        print "timer start"

    def __bind(self):
        self.Bind(wx.EVT_BUTTON, self.OnSettings, self.btnSettings)
        self.Bind(wx.EVT_BUTTON, self.OnClearLog, self.btnClearLog)
        self.Bind(wx.EVT_BUTTON, self.OnAdd, self.btnAdd)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnAdd, self.tclUrl)
        self.Bind(wx.EVT_TIMER, self.updateQueueList)

    def OnAdd(self, evt):
        """
        add movieid/mylistid from self.tclUrl
        """
        url = self.tclUrl.GetValue()
        mid = self.nicoMain.find(url)
        if not mid:
            self.logging("Add: IDが見つかりませんでした")
        elif self.nicoMain.register(mid):
            self.logging(u"Add: %sを登録しました" % mid)
        elif mid[0:2] == u"sm":
            self.nicoMain.getQueueObj().addFront(mid)
            self.logging(u"Add: %sを次に予約しました" % mid)
        self.tclUrl.SetValue("")

    def logging(self, *texts, **indent):
        """
        texts: shown strings
        indent: (indent=True/False) If indent is True, show indent.
        """
        self.output(texts[0])
        self.output("\n")
        #self.log(*texts, **indent)  # raise unknown error

    def OnClearLog(self, evt):
        """
        log Clear
        """
        self.tclLog.SetValue("")
        time.sleep(0.1)

    def OnSettings(self, evt):
        self.dlgSettings.ShowModal()
        #try:
        sdb = SystemDatabase(self.systemDatabasePath)
        sdb.svNicoid(self.nicoTable.getNicoid().encode("utf-8"))
        sdb.svNicopw(self.nicoTable.getNicopw().encode("utf-8"))
        sdb.svGmailid(self.nicoTable.getGmailid().encode("utf-8"))
        sdb.svGmailpw(self.nicoTable.getGmailpw().encode("utf-8"))
        sdb.svSavedir(self.nicoTable.getSavedir().encode("utf-8"))
        sdb.close()

        self.dlgSettings = SettingsDialog(self.nicoTable, self.tclLog.WriteText, self)

    def output(self, text):
        """
        overwrite
        """
        self.tclLog.SetInsertionPointEnd()
        self.tclLog.WriteText(text)

    def __set_properties(self):
        # begin wxGlade: NicoMovieLoadGUI.__set_properties
        self.SetTitle("NicoMovieLoad")
        self.SetSize((700, 650))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: NicoMovieLoadGUI.__do_layout
        sizer0 = wx.BoxSizer(wx.HORIZONTAL)
        sizerButtons = wx.BoxSizer(wx.VERTICAL)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        szrBottom = wx.BoxSizer(wx.HORIZONTAL)
        szrLog = wx.BoxSizer(wx.VERTICAL)
        szrQueueList = wx.BoxSizer(wx.VERTICAL)
        szrUrlTextBox = wx.BoxSizer(wx.HORIZONTAL)
        szrUrlBox = wx.BoxSizer(wx.VERTICAL)
        szrUrlText = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.treeCtrl, 1, wx.EXPAND, 0)
        szrUrlText.Add(self.lblUrl, 1, 0, 0)
        szrUrlTextBox.Add(szrUrlText, 0, wx.EXPAND, 0)
        szrUrlBox.Add(self.tclUrl, 0, wx.EXPAND, 0)
        szrUrlTextBox.Add(szrUrlBox, 1, wx.EXPAND, 0)
        self.pnlCenter.SetSizer(szrUrlTextBox)
        sizer_1.Add(self.pnlCenter, 0, wx.EXPAND, 0)
        szrQueueList.Add(self.lblQueueList, 0, wx.EXPAND, 0)
        szrQueueList.Add(self.lclQueueList, 1, wx.EXPAND, 0)
        szrBottom.Add(szrQueueList, 1, wx.EXPAND, 0)
        szrLog.Add(self.lblLog, 0, wx.EXPAND, 0)
        szrLog.Add(self.tclLog, 1, wx.EXPAND, 0)
        szrBottom.Add(szrLog, 1, wx.EXPAND, 0)
        self.pnlBottom.SetSizer(szrBottom)
        sizer_1.Add(self.pnlBottom, 1, wx.EXPAND, 0)
        sizer0.Add(sizer_1, 1, wx.EXPAND, 0)
        sizer0.Add(self.static_line_1, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 1)
        sizerButtons.Add(self.btnRss, 0, wx.EXPAND, 0)
        sizerButtons.Add(self.btnAdd, 0, wx.EXPAND, 0)
        sizerButtons.Add(self.btnLoad, 0, wx.EXPAND, 0)
        sizerButtons.Add(self.btnClearLog, 0, wx.EXPAND, 0)
        sizerButtons.Add(self.btnDelete, 0, wx.EXPAND, 0)
        sizerButtons.Add(self.btnSettings, 0, wx.EXPAND, 0)
        sizerButtons.Add(self.btnExit, 0, wx.EXPAND, 0)
        self.pnlRight.SetSizer(sizerButtons)
        sizer0.Add(self.pnlRight, 0, wx.EXPAND, 0)
        self.SetSizer(sizer0)
        self.Layout()
        # end wxGlade

    def __setTreeListCtrl(self):
        isz = (16,16)  # image
        il = wx.ImageList(isz[0], isz[1])
        fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
        fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))

        self.treeCtrl.SetImageList(il)
        self.il = il

        # create some columns
        self.treeCtrl.AddColumn(u"タイトル")
        self.treeCtrl.AddColumn(u"済み or RSS")
        self.treeCtrl.AddColumn(u"id")
        self.treeCtrl.SetMainColumn(0) # the one with the tree in it...
        self.treeCtrl.SetColumnWidth(0, 175)
        # append data
        self.treeCtrlRoot = []
        self.root = self.treeCtrl.AddRoot("The Root Item")
        self.treeCtrlRoot.append(self.root)
        #self.treeCtrl.SetItemText(self.root, "col 1 self.root", 1)
        #self.treeCtrl.SetItemText(self.root, "col 2 self.root", 2)
        #self.treeCtrl.SetItemImage(self.root, fldridx, which = wx.TreeItemIcon_Normal)
        #self.treeCtrl.SetItemImage(self.root, fldropenidx, which = wx.TreeItemIcon_Expanded)
        for x in range(5):
            txt = "Item %d" % x
            child = self.treeCtrl.AppendItem(self.root, txt)  # tree part
            self.treeCtrl.SetItemText(child, txt + " do RSS or dont", 1)  # description 1
            self.treeCtrl.SetItemText(child, txt + " mylist id", 2)  # description 2
            self.treeCtrl.SetItemImage(child, fldridx, which = wx.TreeItemIcon_Normal)
            self.treeCtrl.SetItemImage(child, fldropenidx, which = wx.TreeItemIcon_Expanded)
            for i in xrange(5):
                txt2 = "Item"
                last = self.treeCtrl.AppendItem(child, txt2)
                self.treeCtrl.SetItemText(last, txt + " Loaded or yet", 1)  # description 1
                self.treeCtrl.SetItemText(last, txt + " move id", 2)  # description 2
                self.treeCtrl.SetItemImage(last, fileidx, which = wx.TreeItemIcon_Normal)
                self.treeCtrl.SetItemImage(last, fileidx, which = wx.TreeItemIcon_Selected)

    def __set_QueueListCtrl(self):
        self.lclQueueList.InsertColumn(0, u"ID")
        self.lclQueueList.InsertColumn(1, u"title")
        self.lclQueueList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.lclQueueList.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.lclQueueList.OnGetItemText = self.OnGetItemText

    def updateQueueList(self):
        movieQueue = self.nicoMain.getQueueObj.getQueueList()
        print movieQueue
        # 辞書の値の更新
        for movieid in self.__queueDict.keys():
            if not(movieid in movieQueue):
                del self.__queueDict[movieid]
        for movieid in movieQueue:
            if self.__queueDict.has_key(movieid) == False:
                try:
                    api = NicovideoAPI(movie_id=movieid)
                    title = api.get_movie_title()
                except:
                    title = "unknown"
                self.__queueDict.update({movieid : title})

        for movieid, title in self.__queueDict.items():
            self.__queueList.append((movieid, title))
        self.lclQueueList.SetItemCount(len(self.__queueList))

    def appendQueueList(self, mid, title):
        self.__queueList.append((mid, title))
        self.lclQueueList.SetItemCount(len(self.__queueList))

    def OnGetItemText(self, row, col):
        return self.__queueList[row][col]

    def removeQueueList(self):
        self.lclQueueList.DeleteItem(0)

# end of class NicoMovieLoadGUI

if __name__ == "__main__":
    #"""
    app = wx.App(False)
    #wx.InitAllImageHandlers()
    NicoMovieLoadGUI = NicoMovieLoadGUI(None, -1, "NicoMovieLoad")
    #app.SetTopWindow(NicoMovieLoadGUI)
    NicoMovieLoadGUI.Show()
    app.MainLoop()
    #"""
    """
    import os
    import os.path
    from modules.nicoLoad_database import SystemDatabase
    print os.getcwd()
    sysDatabasePath = os.path.join(os.getcwd(), u"nmlsystem.db")
    databasePath = os.path.join(os.getcwd(), u"nmlTest.db")
    db = SystemDatabase(sysDatabasePath)
    db.ctTable()
    db.svNicoid("zeuth717@gmail.com")
    db.svNicopw("kusounkobaka")
    db.svSavedir(os.getcwd())
    db.close()
    nml = NicoMovieLoadMain(databasePath, sysDatabasePath)
    nml.setWtimeLoad(3)
    #nml.setWtimeScan(3)
    #nml.setWtimeRss(3)
    
    nml.register("sm12646949")
    nml.main()
    """


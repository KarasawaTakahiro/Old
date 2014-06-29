# coding: utf-8
'''
Created on 2012/02/19

@author: KarasawaTakahiro
'''

import cgi
import cookielib
import datetime
#import modules.disc_space as discspace
import modules.nicodl_dl as DL
import modules.nicodl_sendmail as SendMail
import modules.nicodl_various as Various
import modules.nicovideoAPI as Nicovideo
import os
import threading
import time
import urllib
import urllib2
import wx
import wx.lib.filebrowsebutton as filebrowse
import wx.lib.rcsizer as rcs

class SettingDialog(wx.Dialog):
    def __init__(self, parent, gmail_id, gmail_pw, nico_id, nico_pw, toaddr, savedir):
        wx.Dialog.__init__(self, parent, title=u'設定', size=(270,215))
        #
        self.gmail_id = gmail_id
        self.gmail_pw = gmail_pw
        self.nico_id = nico_id
        self.nico_pw = nico_pw
        self.toaddr = toaddr
        self.savedir = savedir
        print 'SettingDialog'
        print 'Gmail ID', self.gmail_id
        print 'Gmail PW', '*'*len(self.gmail_pw)
        print 'Nicovideo ID', self.nico_id
        print 'Nicovideo PW', '*'*len(self.nico_pw)
        print 'toAddr', self.toaddr
        print 'Savedir', self.savedir

        # Wigets
        self.gmail_id_st = wx.StaticText(self, label=u'Gmail ID')
        self.gmail_pw_st = wx.StaticText(self, label=u'Gmail PW')
        self.nico_id_st = wx.StaticText(self, label=u'ニコニコ動画 ID')
        self.nico_pw_st = wx.StaticText(self, label=u'ニコニコ動画 PW')
        self.toaddr_st = wx.StaticText(self, label=u'完了メール送信先')
        self.gmail_id_tc = wx.TextCtrl(self, -1, value=self.gmail_id)
        self.gmail_pw_tc = wx.TextCtrl(self, -1, value=self.gmail_pw, style=wx.TE_PASSWORD)
        self.nico_id_tc = wx.TextCtrl(self, -1, value=self.nico_id)
        self.nico_pw_tc = wx.TextCtrl(self, -1, value=self.nico_pw, style=wx.TE_PASSWORD)
        self.toaddr_tc = wx.TextCtrl(self, -1, value=self.toaddr)
        self.dbb = filebrowse.DirBrowseButton(self, -1, labelText=u'フォルダ選択', buttonText=u'参照', changeCallback=self.dbbCallback, newDirectory=True)
        self.dbb.SetValue(self.savedir)
        # parent Sizer
        sizer_parent = wx.BoxSizer(wx.VERTICAL)
        # Sizer
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer = rcs.RowColSizer()
        sizer.Add(self.gmail_id_st, row=0, col=0)
        sizer.Add(self.gmail_id_tc, flag=wx.EXPAND, row=0, col=1, colspan=4)
        sizer.Add(self.gmail_pw_st, row=1, col=0)
        sizer.Add(self.gmail_pw_tc, flag=wx.EXPAND, row=1, col=1, colspan=4)
        sizer.Add(self.nico_id_st, row=2, col=0)
        sizer.Add(self.nico_id_tc, flag=wx.EXPAND, row=2, col=1, colspan=4)
        sizer.Add(self.nico_pw_st, row=3, col=0)
        sizer.Add(self.nico_pw_tc, flag=wx.EXPAND, row=3, col=1, colspan=4)
        sizer.Add(self.toaddr_st, row=4, col=0)
        sizer.Add(self.toaddr_tc, flag=wx.EXPAND, row=4, col=1, colspan=4)
        sizer2.Add(sizer, flag=wx.TOP, border=5)
        sizer2.Add(self.dbb)
        sizer_parent.Add(sizer2)
        # 
        line = wx.StaticLine(self, -1)#, style=wx.LI_HORIZONTAL)
        sizer_parent.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
        # Dialog BUtton
        # OK
        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_OK, label=u'保存')
        btn.SetDefault()
        btnsizer.AddButton(btn)
        # CANCEL 
        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)        
        btnsizer.Realize()
        sizer_parent.Add(btnsizer, 0, flag=wx.ALIGN_CENTER|wx.TOP, border=5)

        self.SetSizer(sizer_parent)
        self.SetAutoLayout(True)
        self.Fit()
        
    def dbbCallback(self, evt):
        pass
    
    def getvalues(self):
        return {'gmail_id':self.gmail_id_tc.GetValue(),
                'gmail_pw':self.gmail_pw_tc.GetValue(),
                'nico_id':self.nico_id_tc.GetValue(),
                'nico_pw':self.nico_pw_tc.GetValue(),
                'toaddr':self.toaddr_tc.GetValue(),
                'savedir':self.dbb.GetValue()
                }

class DownloadInterraptionException(Exception):
    u"""
    *ダウンロードが中止したとき
    """
    def __init__(self):
        pass
    def __str__(self):
        return 'Download was Interrapted'

# 新しいイベントクラスとイベントを定義する
EVT_TYPE_START = wx.NewEventType()  ##
EVT_START = wx.PyEventBinder(EVT_TYPE_START)  ##
EVT_TYPE_FINISH = wx.NewEventType()  ##
EVT_FINISH = wx.PyEventBinder(EVT_TYPE_FINISH)  ##

class DownloadEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid):
        wx.PyCommandEvent.__init__(self, etype, eid)
    def GetValue(self):
        return True

class StartEvent(wx.PyCommandEvent):  ##
    u"""
          ダウンロード開始
    """
    def __init__(self, etype, eid):
        wx.PyCommandEvent.__init__(self, etype, eid)
    def GetValue(self):
        return True

class FinishEvent(wx.PyCommandEvent):  ##
    u"""
         ダウンロード１セット終了
    """
    def __init__(self, etype, eid):
        wx.PyCommandEvent.__init__(self, etype, eid)
    def GetValue(self):
        return True

class nicoDL_mainWindow(wx.Frame):
    u"""
    *メール送信やDL中止のチェック機能を付けた関数を用意して、
    *それをベツの関数からスレッドで呼び出す
    call()　ループ
    download()　DLのみ
    """
    def __init__(self, title="nicoDL", size=(370, 210), pos=wx.DefaultPosition):
        wx.Frame.__init__(self, None, title=title,
                          pos = pos,
                          size = size,
                          style=wx.MAXIMIZE_BOX | wx.RESIZE_BORDER |
                                wx.SYSTEM_MENU | wx.CAPTION |
                                wx.CLOSE_BOX | wx.CLIP_CHILDREN
                                )

        self.cwd = os.getcwd()

        # ICON
        self.tb_ico = wx.TaskBarIcon()
        self.ico = wx.Icon(os.path.join(self.cwd, "data\\nicodl.ico"), wx.BITMAP_TYPE_ICO)
        self.tb_ico.SetIcon(self.ico, u"nicoDL is runnnig!!")

        self.windowtitle = title
        self.libfile_dir = os.path.join(self.cwd, 'data')
        self.infofile_dir = os.path.join(self.cwd, 'data')
        self.nico_id = ''
        self.nico_pw = ''
        self.gmail_id = ''
        self.gmail_pw = ''
        self.toaddr = ''
        self.savedir = os.path.join(self.cwd, 'movies')
        self.infoload()

        # Bind
        self.tb_ico.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.OnRightUp)
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        #

        gauge_len = 300
        # メニュー設定
        self.setmenu()
        # ステータスバー
        self.CreateStatusBar()
        self.SetStatusText('Welcome!!')
        # Panel
        self.panel = wx.Panel(self)
        # ストップ・スタートボタン
        if not hasattr(self, 'btn_ID'):  self.btn_ID = wx.NewId()
        self.btn = wx.Button(self.panel, id=self.btn_ID, label='Start', pos=(0,0))
        # 進行度ゲージ
        self.gauge = wx.Gauge(self.panel, pos=(2,50), size=(gauge_len,10))
        # 進行度文字
        self.par_tt = wx.StaticText(self.panel, pos=(gauge_len+5,47))
        # 動画名
        self.movie_name_st = wx.StaticText(self.panel, pos=(0, 80))
        # メール送信確認チェックボックス
        self.mailcheck_cb = wx.CheckBox(self.panel, label=u'完了メール送信', pos=(100,15))
        if not(self.toaddr == ''):  # 送信先アドレスが設定されている
            self.mailcheck_cb.SetValue(True)
            self.mailcheck = True  # 完了メールを送信するか
        else:
            self.mailcheck = False

        #
        self.running = False  # download()を実行しているか
        # Event
        self.startevt = StartEvent(EVT_TYPE_START, wx.ID_ANY)
        self.finishevt = FinishEvent(EVT_TYPE_FINISH, wx.ID_ANY)
        # Bind
        self.Bind(EVT_START, self.call)
        self.Bind(EVT_FINISH, self.DLstop)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox)
        self.Bind(wx.EVT_BUTTON, self.call, self.btn, id=self.btn_ID)
        # Sizer
        sizer = rcs.RowColSizer()
        sizer.Add(self.btn, row=0, col=0, flag=wx.TOP, border=3)
        sizer.Add(self.mailcheck_cb, row=1, col=0, flag=wx.TOP|wx.LEFT, border=3)
        sizer.Add(self.gauge, row=2, col=0, colspan=4, flag=wx.TOP|wx.LEFT, border=3)
        sizer.Add(self.par_tt, row=3, col=0, flag=wx.TOP|wx.LEFT, border=3)
        sizer.Add(self.movie_name_st, row=4, col=0, flag=wx.TOP|wx.LEFT, border=3)
        #sizer.Add(self., row=, col=)
        self.panel.SetSizer(sizer)
        self.panel.SetAutoLayout(True)

        wx.PostEvent(self, self.startevt)

    def OnSetting(self, evt):
        dlg = SettingDialog(parent=self, gmail_id=self.gmail_id, gmail_pw=self.gmail_pw, nico_id=self.nico_id, nico_pw=self.nico_pw, toaddr=self.toaddr, savedir=self.savedir)
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            print u'情報を保存'
            nicodl = DL.nicoDL_DL(self.infofile_dir)
            infos = dlg.getvalues()
            self.gmail_id = infos['gmail_id']
            self.gmail_pw = infos['gmail_pw']
            self.nico_id = infos['nico_id']
            self.nico_pw = infos['nico_pw']
            self.toaddr = infos['toaddr']
            self.savedir = infos['savedir']
            # 保存
            nicodl.infofilesave(nicodl.mkcliantinfoformat(self.gmail_id, self.gmail_pw, self.nico_id, self.nico_pw, self.toaddr, self.savedir))
            self.myprint('Gmail ID', self.gmail_id)
            self.myprint('Gmail PW', u'*'*len(self.gmail_pw))
            self.myprint('Nicovideo ID', self.nico_id)
            self.myprint('NIcovideo PW', u'*'*len(self.nico_pw))
            self.myprint('toAddr', self.toaddr)
            self.myprint('Savedir', self.savedir)
        else:  print 'Cancel'
        dlg.Destroy()

    def OnCheckBox(self, evt):
        if evt.IsChecked() == 0:
            self.mailcheck = False
        elif evt.IsChecked() == 1:
            self.mailcheck = True
        else: raise ValueError, 'OnCheckBox'

    def PGfill(self, pg_obj, value):
        u"""
        pg_obj: PyGauge Object
        SetValue(塗りつぶす範囲)
        Refresh() 塗りつぶす
        """
        #print 'Fill: %i' % value

        pg = pg_obj
        grange = int(pg.GetRange())
        value = int(value)
        if grange <= value:
            #print 'Fill Over'
            pg.SetValue(grange)
        else:
            pg.SetValue(value)
        pg.Refresh()

    def call(self, event):
        u"""
        download()を呼ぶ関数
        """
        if self.running == False:
            print 'Start'
            th1 = threading.Thread(target=self.download)
            th1.setDaemon(True)
            th1.start()
            self.DLstart()
        else:  self.DLstop()

    def DLstart(self):
        u"""
        DL時の初期化はココで行なう
        """
        self.running = True
        self.btn.SetLabel('Stop')
        self.gauge.SetValue(0)
        self.gauge.Refresh()
        self.par_tt.SetLabel('0%')
        self.movie_name_st.SetLabel(u'動画名')
        self.SetStatusText(u'準備中')

    def DLstop(self):
        self.running = False
        self.btn.SetLabel('Start')
        self.gauge.SetValue(0)
        self.gauge.Refresh()
        self.par_tt.SetLabel('0%')
        self.movie_name_st.SetLabel(u'動画名')
        self.SetStatusText(u'待機中')
        print 'Stop'

    def checkdir(self, savedir):
        """
        savedir: 保存フォルダ
        return 
            savedirが空いてる　  => 保存フォルダ
            savedirが空いてない => False
        """
        # 保存場所決定
        if os.path.exists(savedir): pass 
        else:
            # savedirがなければcdir\movieに保存
            print u'見つからず'
            savedir = os.path.join(self.cwd, 'movie')
        # 空きチェック
        #if discspace.free_disk_space(savedir)[0] > 1: return savedir
        #else: return False
        return savedir

    def movie_dl(self, myformat, mylist_id=False):
        u"""
        *動画を保存する関数.
        myformat: 動画IDを渡したmyformatオブジェクト
        mylist_id: mylist ID
        """
        buffer_size = 8 * 1024

        # ログイン
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        req = urllib2.Request("https://secure.nicovideo.jp/secure/login")
        req.add_data(urllib.urlencode({"mail":self.nico_id, "password":self.nico_pw}))
        res = opener.open(req)
        # 動画配信場所取得(getflv)
        res = opener.open("http://flapi.nicovideo.jp/api/getflv/"+myformat.movie_id).read()
        videoURL = cgi.parse_qs(res)["url"][0]
        # 動画のダウンロード
        opener.open("http://www.nicovideo.jp/watch/"+myformat.movie_id)  # 必要
        res = opener.open(videoURL)
        ext = res.info().getsubtype()
        # 動画名決定
        if myformat.movie_name:
            title = myformat.movie_name
        else:
            nicoapi = Nicovideo.Nicovideo(movie_id=myformat.movie_id)
            title = nicoapi.get_movie_title()
        various = Various.nicoDL_Various()
        title = various.filenamecheck(title);  del various
        # フォルダ名決定
        if mylist_id:
            # マイリスから
            various = Various.nicoDL_Various(self.libfile_dir)
            mylistname = various.pickup(mylist_id=mylist_id, choice='mylist_name')
            if mylistname == False:
                """マイリス名を取得していない場合"""
                nicoapi = Nicovideo.Nicovideo(mylist_id=mylist_id)
                # マイリス名取得
                mylistname = nicoapi.get_mylist_name()
                # ライブラリ書き換え
                various.rewrite_library(factor='mylist_name', value=mylistname,  mylist_id=mylist_id)
            """ファイルに使用不可な文字列を除外し、パス生成"""
            savedir = os.path.join(self.savedir, 
                                   various.filenamecheck(mylistname))
            if not os.path.exists(savedir):
                # フォルダが無ければ作成
                os.makedirs(savedir)
            #print savedir
            #print title
            filename = os.path.join(savedir, title+"."+ext)
        else:  filename = os.path.join(self.savedir, title+"."+ext)
        # 動画サイズ
        nicoapi = Nicovideo.Nicovideo(movie_id=myformat.movie_id)
        if videoURL.find('low') == -1:  # 画質high
            size = nicoapi.get_movie_size_high()
        elif videoURL.find('low') > -1:  # 画質low
            size = nicoapi.get_movie_size_low()
        else:  raise DownloadInterraptionException()
        # 書き込み
        ofh = open(filename,"wb", buffer_size)
        try:
            while int(ofh.tell()) < size:
                # ファイルに書き込み
                ofh.write(res.read(buffer_size))
                par = (float(ofh.tell())/float(size))*100
                # ゲージ塗りつぶし
                self.PGfill(self.gauge, par)
                # statusbar
                self.SetStatusText(u"Finish: %s/%s" % (str(ofh.tell()), size))
                # %書き換え
                self.par_tt.SetLabel(u'%i%%' % par)
                if self.running == False:
                    ofh.close()
                    os.remove(filename)
                    raise DownloadInterraptionException()
        except DownloadInterraptionException:
            raise DownloadInterraptionException()
        finally:
            #print 'File close'
            if ofh.closed == False:  ofh.close()

        return filename

    def download(self):
        u"""
        *ダウンロードの全体を統括する関数.
        *一通り終わったら、ループせずにself.running=Falseにする
        """
        self.DLstart()

        nicodl = DL.nicoDL_DL(self.infofile_dir)
        various = Various.nicoDL_Various(self.libfile_dir)
        while True:
            try:
                print u'Gmailにアクセスしています...'
                myformat = nicodl.geturl()  # Gmailチェック
                self.SetStatusText(u'Gmailにログイン')
                break
            except:
                self.SetStatusText(u'Gmailにログインできませんでした...')
                myformat = False
                break
        #print "myformat:", myformat
        if myformat == False: pass # Gamilが空
        else:
            # library_ALL.ndl に追加
            various.write_library(myformat)

        while True:
            if self.checkdir(self.savedir): 
                self.savedir = self.checkdir(self.savedir) 
                break 
            else:
                # 空き容量不足でループをリセット
                print u"空き容量不足:\n ->%s" % self.savedir
                time.sleep(3)
                self.DLstop()
                if not self.running:
                    return
                continue

        print self.savedir, u"に保存"
        if not self.running:  return

        # RSS
        print u"RSSチェック中..."
        self.SetStatusText(u"RSSチェック中...")
        various.rsscheck()
        self.SetStatusText(u"RSSチェック完了")
        print u"RSSチェック完了!"

        """DL部分"""
        # 動画IDが保存されていない
        if various.getmovieIDs() == []:
            self.DLstop()
            wx.PostEvent(self, self.startevt)
            return
        # DL対象を決定
        movies = []
        for item in various.getmovieIDs():
            if not (various.pickup(movie_id=item, choice='state')):
                movies.append(item)

        for movie in movies:
            if not self.running:  return

            movie_obj = various.pickup(movie_id=movie)  # obj

            if movie_obj.mylist_id != False:
                # マイリスから
                mylistflag = movie_obj.mylist_id
                nico = Nicovideo.Nicovideo(movie_id=movie_obj.movie_id,
                                           mylist_id=movie_obj.mylist_id)
            else:
                # マイリスからじゃない
                mylistflag = False
                nico = Nicovideo.Nicovideo(movie_id=movie_obj.movie_id)

            # 情報取得
            if movie_obj.movie_name: title = movie_obj.movie_name
            else: title = nico.get_movie_title()
            self.movie_name_st.SetLabel(title)  # 動画名セット
            description = nico.get_movie_description()  #
            self.myprint(movie_obj.movie_id, title)
            # 終了時間計算
            length = nico.get_movie_length()
            minute = int(length.split(':')[0])
            second = int(length.split(':')[1])
            now = datetime.datetime.now()
            end = now + datetime.timedelta(minutes=minute, seconds=second)
            end = end.strftime(u'%m/%d %H:%M')
            self.myprint(movie_obj.movie_id, "".join([end, u"頃終了します."]))
            # サムネ保存
            self.myprint(movie_obj.movie_id, u" サムネイル取得中...")
            self.SetStatusText(u'サムネイル取得中...')
            thumbnail = nico.save_thumbnail(os.path.join(self.cwd, "data\\thumbnail"))
            # 動画保存
            self.myprint(movie_obj.movie_id, u" 動画取得中...")
            self.SetStatusText(u'動画取得中...')
            self.SetTitle(u'%s - %s - %s' % (self.windowtitle, movie_obj.movie_id, end))
            try:  movie_path = self.movie_dl(myformat=movie_obj, mylist_id=mylistflag)
            except DownloadInterraptionException:
                print 'download() raise DLExcept'
                self.DLstop()
                return
            self.myprint(movie_obj.movie_id, "".join([u" 動画取得完了!"]))#, "\n =>", movie_path]))
            # コメント保存
            self.myprint(movie_obj.movie_id, u" コメント取得中...")
            self.SetStatusText(u'コメント取得中...')
            ff = open(os.path.splitext(movie_path)[0] + '.xml', 'w')
            ff.write(nico.get_comment(self.nico_id, self.nico_pw, 1000))
            ff.close()
            # 情報書き換え
            self.myprint(movie_obj.movie_id, u"情報を更新します...")
            various.rewrite_library(factor="thumbnail", value=thumbnail, movie_id=movie_obj.movie_id)
            various.rewrite_library(factor="state", value=True, movie_id=movie_obj.movie_id)
            various.rewrite_library(factor="movie_path", value=movie_path, movie_id=movie_obj.movie_id)
            # マイリスが登録されていたらそのマイリスのDL済みに追加
            if movie_obj.mylist_id != False:
                ed = various.pickup(mylist_id=movie_obj.mylist_id, choice='downloaded')
                if not(movie_obj.movie_id in ed):  # 入ってないとき
                    various.rewrite_library(factor="downloaded", value=movie_obj.movie_id, mylist_id=movie_obj.mylist_id)
            # メール送信
            if self.mailcheck:
                self.myprint(movie_obj.movie_id, u" 完了メール送信")
                mail = SendMail.nicodl_sendmail(self.gmail_id, self.gmail_pw, self.toaddr)
                mail.main("".join([title, "\n\n", description]), movie_obj.movie_id)
            #nicodl.extention()  # 拡張
            #break
            print u"次..."
            time.sleep(3)
        self.DLstop()
        print u'1セット終了'
        for i in xrange(300, 0):
            self.SetStatusText(u'待機中...残り%i秒' % i)
            time.sleep(1)
        wx.PostEvent(self, self.finishevt)
        wx.PostEvent(self, self.startevt)

    def setmenu(self):
        # menu_setting
        menu_setting = wx.Menu()
        # menuItem_setting
        self.menuItem_settingID = wx.NewId()
        menu_setting.Append(id=self.menuItem_settingID, text=u'設定')
        
        menuBar = wx.MenuBar()
        menuBar.Append(menu_setting, u'メニュー')
        
        self.SetMenuBar(menuBar)
        
        self.Bind(wx.EVT_MENU, self.OnSetting, id=self.menuItem_settingID)

    def myprint(self, ID, mess):
        u"""
        *表示用フォーマット
        """
        print u'[%s] %s' % (ID, mess)

    def infoload(self):
        """
       　　　　 データの読み込み
       　　　　最初にやる
        """
        try:
            nicodl = DL.nicoDL_DL(self.infofile_dir)
    
            self.nico_id = nicodl.pickup('nico_id')
            self.nico_pw = nicodl.pickup('nico_pw')
            self.gmail_id = nicodl.pickup('gmail_id')
            self.gmail_pw = nicodl.pickup('gmail_pw')
            self.toaddr = nicodl.pickup('toaddr')
            self.savedir = os.path.join(nicodl.pickup('savedir'))#, 'movies')
        except:
            # エラー
            print 'load error'

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
        *バツ押したとき
        """
        #print "CloseEvent"
        self.Hide()
        #self.Destroy()  ##

    def OnExitApp(self, evt):
        self.tb_ico.Destroy()
        self.Destroy()


if __name__ == '__main__':
    print 'Start'
    app = wx.App(False)#True, r'C:\Users\KarasawaTakahiro\workspace\nicoDL3\src\out.txt')
    win = nicoDL_mainWindow()
    win.Show()
    app.MainLoop()

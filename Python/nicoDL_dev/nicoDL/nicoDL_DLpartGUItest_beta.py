#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import pickle
import sys
import threading
import wx

import cgi
import cookielib
import urllib
import urllib2

import datetime
import free_disc_space as freespace
import nicodl_dl as DL
import nicodl_various_beta as Various
import nicodl_sendmail as SendMail
import nicovideo as Nicovideo
import os.path
import sys
import time
try:
    from agw import pygauge as PG
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.pygauge as PG


class DownloadInterraptionException(Exception):
    u"""
    ダウンロードが中止したとき
    """
    def __init__(self):
        pass
    def __str__(self):
        return 'Downlard was Interrapted'

class RedirectText(object):
    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl

    def write(self,string):
        self.out.WriteText(string)


# 新しいイベントクラスとイベントを定義する
EVT_TYPE_DL = wx.NewEventType()
EVT_DL = wx.PyEventBinder(EVT_TYPE_DL)
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
    def __init(self, etype, eid):
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


class nicoDL_mainWindow(wx.Panel):
    u"""
    メール送信やDL中止のチェック機能を付けた関数を用意して、
    それをベツの関数からスレッドで呼び出す
    call()　ループ
    download()　DLのみ
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        gauge_len = 300
        # ストップ・スタートボタン
        self.btn = wx.Button(self, label='Start', pos=(0,0))
        # 進行度ゲージ
        self.gauge = PG.PyGauge(self, pos=(2,50), size=(gauge_len,10))
        self.gauge.SetBackgroundColour(wx.WHITE)
        # 進行度文字
        self.par_tt = wx.StaticText(self, pos=(gauge_len+5,47))#, label='---%')
        # 動画名
        self.movie_name = wx.StaticText(self, pos=(0, 80))#, label='動画名')
        # メール送信確認チェックボックス
        self.mailcheck_cb = wx.CheckBox(self, label='完了メール送信', pos=(100,15))
        self.mailcheck_cb.SetValue(True)
        #
        self.running = False  # download()を実行しているか
        self.run_continue = True  # download()を続けるか
        self.cwd = os.getcwd()
        self.lib_filedir = self.cwd  # ライブラリファイルのある場所
        self.mailcheck = True
        self.startevt = StartEvent(EVT_TYPE_START, wx.ID_ANY)
        self.finishevt = FinishEvent(EVT_TYPE_FINISH, wx.ID_ANY)
        # Bind
        self.Bind(EVT_START, self.call)
        self.Bind(EVT_FINISH, self.call)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox)
        self.btn.Bind(wx.EVT_BUTTON, self.run_continue_chenge)

        wx.PostEvent(self, self.startevt)

    def OnCheckBox(self, evt):
        if evt.IsChecked() == 0:
            self.mailcheck = False
        elif evt.IsChecked() == 1:
            self.mailcheck = True
        else: raise ValueError, 'OnCheckBox'


    def PGfill(self, pg_obj,value):
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
            print 'Fill Over'
            pg.SetValue(grange)
        else:
            pg.SetValue(value)
        pg.Refresh()

    def run_continue_chenge(self, evt):
        self.run_continue = not self.run_continue
        print 'run_continue:', self.run_continue
        self.call(None)

    def call(self, event):
        u"""
        download()を呼ぶ関数
        """
        if self.run_continue:
            if self.running == False:
                print 'Start'
                th1 = threading.Thread(target=self.download)
                th1.setDaemon(True)
                th1.start()
                self.DLstart()
            else: pass
        else: self.DLstop()

    def DLstart(self):
        u"""
        DL時の初期化はココで行なう
        """
        self.running = True
        self.btn.SetLabel('Stop')
        self.gauge.SetValue(0)
        self.gauge.Refresh()
        self.par_tt.SetLabelText('---%')
        self.movie_name.SetLabelText('動画名')

    def DLstop(self):
        self.running = False
        self.btn.SetLabel('Start')
        self.gauge.SetValue(0)
        self.gauge.Refresh()
        self.par_tt.SetLabelText('0%')
        print 'Stop'

    def movie_dl(self, nico_obj, nicovideo_id, nicovideo_pw, savedir, mylist_id=False):
        u"""
        動画を保存する関数.
        nico_obj: 動画IDを渡したnicovideoオブジェクト
        mylist_id: mylist ID
        """
        nico = nico_obj
        buffer_size = 8 * 1024

        # ログイン
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        req = urllib2.Request("https://secure.nicovideo.jp/secure/login")
        req.add_data(urllib.urlencode({"mail":nicovideo_id, "password":nicovideo_pw}))
        res = opener.open(req)
        # 動画配信場所取得(getflv)
        res = opener.open("http://flapi.nicovideo.jp/api/getflv/"+nico.movie_id).read()
        videoURL = cgi.parse_qs(res)["url"][0]
        # 動画のダウンロード
        opener.open("http://www.nicovideo.jp/watch/"+nico.movie_id)  # 必要
        res = opener.open(videoURL)
        ext = res.info().getsubtype()
        title = nico.get_movie_title()
        # 動画名決定
        if mylist:
            # マイリスから
            various = Various.nicoDL_Various(self.lib_filedir)
            mylistname = various.pickup(mylist_id=mylist_id, choice='mylist_name')
            if not os.path.exists(os.path.join(savedir, mylistname)):
                # フォルダが無ければ作成
                os.mkdir(os.path.exists(os.path.join(savedir, mylistname)))
            filename = os.path.join(savedir, mylistname, title+"."+ext)
        else:  filename = os.path.join(savedir, title+"."+ext)

        # 動画サイズ
        if videoURL.find('low') == -1:  # 画質high
            size = nico.get_movie_size_high()
        elif videoURL.find('low') > -1:  # 画質low
            size = nico.get_movie_size_low()
        else:
            raise DownloadInterraptionException()

        # 書き込み
        ofh = open(filename,"wb", buffer_size)
        try:
            while int(ofh.tell()) < size:
                print "Finish: %s/%s" % (str(ofh.tell()), size)
                # ファイルに書き込み
                ofh.write(res.read(buffer_size))
                par = (float(ofh.tell())/float(size))*100
                # ゲージ塗りつぶし
                self.PGfill(self.gauge, par)
                # %書き換え
                self.par_tt.SetLabelText('%i%%' % par)
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
        ダウンロードの全体を統括する関数.
        一通り終わったら、ループせずにself.running=Falseにする
        """
        self.DLstart()

        nicodl = DL.RemoteNicovideoDL('myremote717@gmail.com', 'kusounkobaka',
                                      'zeuth717@gmail.com', 'kusounkobaka',
                                      'zeuth717@gmail.com',
                                      r'E:\Takahiro\ndl_test')
        various = Various.nicoDL_Various(self.lib_filedir)
        dlevt = DownloadEvent(EVT_TYPE_DL, wx.ID_ANY)


        myformat = nicodl.geturl()  # Gmailチェック
        print "myformat:", myformat
        if myformat == False: pass # Gamilが空
        else:
            # library_ALL.ndl に追加
            various.write_library(myformat)
            # various.UPDATE() 後で実装

        while True:
            #####################
            if nicodl.mycheckdir(): break
            #####################
            elif os.path.splitdrive(nicodl.savedir)[0].upper() == 'E:': break;
            else:
                # 空き容量不足でループをリセット
                print u"空き容量不足:\n ->%s" % nicodl.savedir
                #time.sleep(300)
                self.DLstop()
                if self.running == False:
                    return
                continue

        print nicodl.savedir, u"に保存"


        # ライブラリファイルリフレッシュ
        #print u"ライブラリリフレッシュ中..."
        #various.reflesh_libraryfile()
        #print u"ライブラリリフレッシュ終了!"
        # RSS
        print u"RSSチェック中..."
        various.rsscheck()
        print u"RSSチェック完了!"

        # DL部分
        movies = various.getmovieIDs()
        if movies == []:
            # 動画IDが保存されていない
            self.DLstop()
            return
        movie = True  ### 終わったら消す
        for movie in movies:
                wx.PostEvent(self, dlevt)

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

                # display
                nicodl.movie_id_display = movie_obj.movie_id  #
                wx.PostEvent(self, dlevt)
                #nicodl.options_display = item["options"]  #
                # 情報取得
                title = nicodl.title_display = nico.get_movie_title()  #
                self.movie_name.SetLabelText(title)  # 動画名セット
                #
                description = nicodl.description_display = nico.get_movie_description()  #
                wx.PostEvent(self, dlevt)
                self.myprint(movie_obj.movie_id, title)
                length = nico.get_movie_length()
                minute = int(length.split(':')[0])
                second = int(length.split(':')[1])
                now = datetime.datetime.now()
                end = now + datetime.timedelta(minutes=minute, seconds=second)
                end = end.strftime('%m/%d %H:%M')
                self.myprint(movie_obj.movie_id, "".join([end, u"頃終了します."]))
                # サムネ保存
                self.myprint(movie_obj.movie_id, u" サムネイル取得中...")
                thumbnail = nicodl.thumbnail_display = nico.save_thumbnail(os.path.join(nicodl.cdir, "data\\thumbnail"))
                wx.PostEvent(self, dlevt)
                # 動画保存
                self.myprint(movie_obj.movie_id, u" 動画取得中...")
                try:  movie_path = self.movie_dl(nico, nicodl.nicoid, nicodl.nicopw, nicodl.savedir, mylist_id=mylistflag)
                except DownloadInterraptionException:
                    print 'download() raise DLExcept'
                    self.DLstop()
                    return
                self.myprint(movie_obj.movie_id, "".join([u" 動画取得完了!", "\n=>", movie_path]))
                # 情報書き換え
                self.myprint(movie_obj.movie_id, u" 情報を更新します...")
                various.rewrite_library(factor="thumbnail", value=thumbnail, movie_id=movie_obj.movie_id)
                various.rewrite_library(factor="state", value=True, movie_id=movie_obj.movie_id)
                various.rewrite_library(factor="movie_path", value=movie_path, movie_id=movie_obj.movie_id)
                # マイリスが登録されていたらそのマイリスのDL済みに追加
                if movie_obj.mylist_id != False:
                    ed = various.pickup(mylist_id=mylist_id, choice='downloaded')
                    if not(movie_obj.movie_id in ed):  # 入ってないとき
                        various.rewrite_library("downloaded", movie_obj.movie_id, mylist_id=movie_obj.mylist_id)
                # メール送信
                if self.mailcheck:
                    self.myprint(movie_obj.movie_id, u" 完了メール送信")
                    mail = SendMail.nicodl_sendmail(nicodl.gid, nicodl.gpw, nicodl.toaddr)
                    mail.main("".join([title, "\n\n", description]), movie_obj.movie_id)
                #nicodl.extention()  # 拡張
                # 外部表示用アトリビュートリセット
                nicodl.movie_id_display = u"動画ID"
                nicodl.title_display = u"タイトル"
                nicodl.description_display = u"動画説明"
                nicodl.options = u"オプション"
                nicodl.thumbnail_display = False
                nicodl.display_download = 0
                wx.PostEvent(self, dlevt)
                #break
                print u"次..."
                #time.sleep(3)
        print u'1セット終了'
        #time.sleep(3)
        wx.PostEvent(self, self.finishevt)

    def myprint(self, ID, mess):
        u"""
        表示用フォーマット
        """
        print u'[%s] %s' % (ID, mess)


class nicoDL(wx.Frame):
    def __init__(self, size=(350, 160),#wx.DefaultSize,
                 pos=wx.DefaultPosition, *args, **kwds):
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

        self.win_main = nicoDL_mainWindow(self)

        # Bind
        self.Bind(EVT_DL, self.display_reserve)
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.Show()  # 起動時に表示するか

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
        ##self.Hide()
        self.Destroy()  ##

    def OnExitApp(self, evt):
        """
        終了処理
        """
        try:
            f = open("data\\info.ndl")
            info = pickle.load(f)
            f.close()
            info["window_pos"] = (self.mypos.x, self.mypos.y)
            info["window_size"] = (self.mysize.width, self.mysize.height)
            f = open("data\\info.ndl", "w")
            pickle.dump(info, f)
            f.close()
        except AttributeError:
            pass

        self.tb_ico.Destroy()
        self.Destroy()


if __name__ == '__main__':
    app = wx.App()
    nicodl = nicoDL()
    app.MainLoop()





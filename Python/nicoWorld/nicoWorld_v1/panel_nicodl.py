
# coding: utf-8
"""
created on 2012/03/27
created by KarasawaTakahiro
"""

import cookielib
import modules.formats as Formats
import modules.nicodl_sendmail as Sendmail
import modules.nicodl_various as Various
import modules.nicovideoAPI as nicoAPI
import os
import pickle
import threading
import time
import urllib
import urllib2
import wx
import wx.lib.filebrowsebutton as filebrowse
import wx.lib.mixins.listctrl as listmix
import images


LIBRARYFILENAME = 'Library.nco'
WAITTIME = 300

"""イベント定義"""
class EVT_Reload(wx.PyCommandEvent):
    u"""
    reloadしてもらう
    """
    def __init__(self, etype, eid):
        wx.PyCommandEvent.__init__(self, etype, eid)
    def GetValue(self):
        return True
EVT_TYPE_RELOAD = wx.NewEventType()
EVT_RELOAD = wx.PyEventBinder(EVT_TYPE_RELOAD)
EVT_RELOADobj = EVT_Reload(EVT_TYPE_RELOAD, wx.ID_ANY)
""" """

"""ListCtrl"""
class ListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.LC_REPORT
                                           | wx.BORDER_NONE
                                           | wx.LC_EDIT_LABELS
                                           | wx.LC_SORT_ASCENDING):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

class nicoDL_MovieListCtrl(wx.Panel, listmix.ColumnSorterMixin):
    def __init__(self, log, libraryfilepath, libraryfilename, parent, style=wx.WANTS_CHARS):
        wx.Panel.__init__(self, parent=parent, style=style)
        self.libraryfilepath = libraryfilepath
        self.libraryfilename = libraryfilename
        self.formats = Formats.LibraryFormat(libraryfilepath=libraryfilepath, libraryfilename=libraryfilename)
        self.selected = None

        self.log = log
        # Wigets
        self.listctrl = ListCtrl(self)
        self.imli = wx.ImageList(16, 16)
        self.sm_up = self.imli.Add(images.SmallUpArrow.GetBitmap())
        self.sm_dn = self.imli.Add(images.SmallDnArrow.GetBitmap())
        self.load()
        listmix.ColumnSorterMixin.__init__(self, 5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.listctrl, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer)

        # for wxMSW
        self.listctrl.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)
        # for wxGTK
        self.listctrl.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)
        
        self.Bind(EVT_RELOAD, self.load)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelected)

    def OnSelected(self, evt):
        self.selected = evt.GetIndex()

    def load(self):
        self.listctrl.DeleteAllColumns()
        self.listctrl.DeleteAllItems()
        self.listctrl.InsertColumn(0, u'ID')
        self.listctrl.InsertColumn(1, u'タイトル')
        self.listctrl.InsertColumn(2, u'DL')
        self.listctrl.InsertColumn(3, u'説明')
        self.listctrl.InsertColumn(4, u'マイリスト')
        self.itemDataMap = {}
        
        data = self.formats.getAllMovieMyformat()
        no = 0
        for item in data:
            self.itemDataMap.update({no:(item.ID, item.title, str(item.state), item.description, item.mylist_id)})
            no += 1
        index = self.listctrl.GetItemCount()
        for key, value in self.itemDataMap.items():
            dist = self.listctrl.InsertStringItem(index, value[0])
            try:
                self.listctrl.SetStringItem(dist, 1, value[1])
                self.listctrl.SetStringItem(dist, 2, value[2])
                self.listctrl.SetStringItem(dist, 3, value[3][0:50])
                self.listctrl.SetStringItem(dist, 4, value[4])
                self.listctrl.SetItemData(index, key)
            except TypeError:
                self.listctrl.SetStringItem(dist, 1, str(value[1]))
                self.listctrl.SetStringItem(dist, 2, str(value[2]))
                self.listctrl.SetStringItem(dist, 3, str(value[3][0:50]))
                self.listctrl.SetStringItem(dist, 4, str(value[4]))
                self.listctrl.SetItemData(index, key)
            index += 1
        self.listctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.listctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.listctrl.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self.listctrl.SetColumnWidth(3, 500)
        self.listctrl.SetColumnWidth(4, wx.LIST_AUTOSIZE)
        self.listctrl.SetColumnWidth(5, wx.LIST_AUTOSIZE)

    def rewrite(self, col, value):
        """
        col: self.load()を参照して選択
        value: 変更する値
        """
        if self.selected or self.selected == 0:
            movie_id = self.itemDataMap[self.selected][0]
        else:  return 
        print self.selected
        print col
        print value
        if (col == 2) or (col == 'state'):
            factor = 'state'
            col = 2
        elif (col == 3) or (col == 'description'):
            factor = 'description'
            col = 3
        elif (col == 4) or (col == 'mylist_id'):
            factor = 'mylist_id'
            col = 4
        else:  raise ValueError, u'myformatとの該当なし'
        self.listctrl.SetStringItem(index=self.selected, col=col, label=unicode(value))
        self.formats.rewrite(myformat=self.formats.getMovieMyformat(movie_id), factor=factor, value=value)

    """右クリックメニュー"""
    def OnRightClick(self, evt):
        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            self.popupID3 = wx.NewId()
            #self.popupID4 = wx.NewId()
            #self.popupID5 = wx.NewId()
            #self.popupID6 = wx.NewId()

            self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
            self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
            self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
            #self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
            #self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
            #self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)

        # make a menu
        menu = wx.Menu()
        # add some items
        menu.Append(self.popupID1, u"リセット")
        menu.Append(self.popupID2, u"削除")
        menu.Append(self.popupID3, u"更新")
        #menu.Append(self.popupID4, "DeleteAllItems")
        #menu.Append(self.popupID5, "GetItem")
        #menu.Append(self.popupID6, "Edit")

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu)
        menu.Destroy()

    def OnPopupOne(self, evt):
        """リセット"""
        self.rewrite(col='state', value=False)
        self.formats.reset(myformat=self.formats.getMovieMyformat(self.itemDataMap[self.selected][0]))
        print u'OnPopupOne'
    def OnPopupTwo(self, evt):
        self.log.write(u'OnPopupTwo')
    def OnPopupThree(self, evt):
        self.log.write(u'OnPopupThree')
    """ """
    """Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py"""
    def GetListCtrl(self):
        return self.listctrl

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.sm_dn, self.sm_up)
    """ """

class nicoDL_MylistListCtrl(wx.Panel, listmix.ColumnSorterMixin):
    def __init__(self, log, libraryfilepath, libraryfilename, parent, style=wx.WANTS_CHARS):
        wx.Panel.__init__(self, parent=parent, style=style)

        self.formats = Formats.LibraryFormat(libraryfilepath=libraryfilepath, libraryfilename=libraryfilename)

        self.log = log
        self.listctrl = ListCtrl(self)
        self.imli = wx.ImageList(16, 16)
        self.sm_up = self.imli.Add(images.SmallUpArrow.GetBitmap())
        self.sm_dn = self.imli.Add(images.SmallDnArrow.GetBitmap())
        self.load()
        listmix.ColumnSorterMixin.__init__(self, 5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.listctrl, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer)

        # for wxMSW
        self.listctrl.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)
        # for wxGTK
        self.listctrl.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)

        self.Bind(EVT_RELOAD, self.load)


    def load(self):
        self.listctrl.DeleteAllColumns()
        self.listctrl.DeleteAllItems()

        self.listctrl.InsertColumn(0, u'ID')
        self.listctrl.InsertColumn(1, u'タイトル')
        self.listctrl.InsertColumn(2, u'RSS')
        self.listctrl.InsertColumn(3, u'説明')
        self.itemDataMap = {}

        no = 0
        for item in self.formats.getAllMylistMyformat():
            self.itemDataMap.update({no:(item.ID, item.title, str(item.rss), item.description)})
            no += 1
        #print self.itemDataMap
        index = self.listctrl.GetItemCount()
        for key, value in self.itemDataMap.items():
            dist = self.listctrl.InsertStringItem(index, value[0])
            try:
                self.listctrl.SetStringItem(dist, 1, value[1])
                self.listctrl.SetStringItem(dist, 2, value[2])
                self.listctrl.SetStringItem(dist, 3, value[3][0:50])
                self.listctrl.SetItemData(index, key)
            except TypeError:
                self.listctrl.DeleteItem(dist)
            index += 1
        self.listctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.listctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.listctrl.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self.listctrl.SetColumnWidth(3, 500)

    """右クリックメニュー"""
    def OnRightClick(self, evt):
        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            self.popupID3 = wx.NewId()
            #self.popupID4 = wx.NewId()
            #self.popupID5 = wx.NewId()
            #self.popupID6 = wx.NewId()

            self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
            self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
            self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
            #self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
            #self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
            #self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)

        # make a menu
        menu = wx.Menu()
        # add some items
        menu.Append(self.popupID1, u"リセット")
        menu.Append(self.popupID2, u"削除")
        menu.Append(self.popupID3, u"RSS変更")
        #menu.Append(self.popupID4, "DeleteAllItems")
        #menu.Append(self.popupID5, "GetItem")
        #menu.Append(self.popupID6, "Edit")

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu)
        menu.Destroy()

    def OnPopupOne(self, evt):
        self.log.write(u'OnPopupOne')
    def OnPopupTwo(self, evt):
        self.log.write(u'OnPopupTwo')
    def OnPopupThree(self, evt):
        self.log.write(u'OnPopupThree')
    """ """
    """Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py"""
    def GetListCtrl(self):
        return self.listctrl

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.sm_dn, self.sm_up)
    """ """
""" """
"""Download"""
class nicoDL_Download(wx.Panel):
    INFOFILE = os.getcwd()
    SUBFOLDER = u'tempolary'
    BUFFERSIZE = 8 * 1024

    def __init__(self, log, libraryfilepath, libraryfilename, parentframe, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        if kwargs.has_key('parent'):  self.parent = kwargs['parent']
        else:  self.parent = args[0]
        self.running = False
        self.stop = False

        #
        self.various = Various.nicoDL_Various(log=True, libraryfilepath=libraryfilepath, libraryfilename=libraryfilename)
        self.libformats = Formats.LibraryFormat(libraryfilepath=libraryfilepath, libraryfilename=libraryfilename)
        self.libformats.load()
        self.infoobj = Formats.InfoFormats(self.INFOFILE)
        self.infoobj.load()
        self.frame = parentframe

        # Wigets
        self.log = log
        self.btn = wx.Button(self, label='Start')
        self.cb = wx.CheckBox(self, label=u'完了メール送信 , ', pos=(-1, 5))
        self.cb.SetValue(True)
        self.st_title = wx.StaticText(self, label=u'')
        self.st_time = wx.StaticText(self, label=u'')

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.btn, 0, border=3, flag=wx.EXPAND|wx.WEST)
        sizer.Add(self.cb, 0, border=3, flag=wx.EXPAND|wx.WEST)
        sizer.Add(self.st_title, 0, border=3, flag=wx.EXPAND|wx.WEST|wx.TOP)
        sizer.Add(wx.StaticText(self, label=u' , '), 0, border=3, flag=wx.EXPAND|wx.WEST|wx.TOP)
        sizer.Add(self.st_time, 0, border=3, flag=wx.EXPAND|wx.TOP)
        self.SetSizerAndFit(sizer)

        self.Bind(wx.EVT_BUTTON, self.OnButton, self.btn)

        self.call()

    def download(self):
        try:
            self.running = True

            dllist = []  # DL対象

            self.checkdiscontinue()

            """
            mail チェック
            *ライブラリ登録
            """
            try:
                myformat = self.various.geturl(self.infoobj.gmail_id, self.infoobj.gmail_pw)
            except:
                self.log.write(u'Gmailにログインできませんでした。')
                self.stop = True
                try:  self.checkdiscontinue()
                except:  return False
            if myformat:
                self.libformats.append(myformat)
                if myformat.type == 'MYLIST':
                    self.various.reloadmylistdata(myformat)
                elif myformat.type == 'MOVIE':
                    self.various.reloadmoviedata(myformat)
            else:  self.log.write(u'新規データはありませんでした。')

            self.checkdiscontinue()

            api = nicoAPI.Nicovideo()
            login = api.logintest(ID=self.infoobj.nico_id, PW=self.infoobj.nico_pw)
            if not login:
                self.log.write(u'ニコニコ動画にログインできませんでした。')
                self.stop = True
                self.checkdiscontinue()

            """
            RSSチェック
            *ライブラリ登録
            """
            for mylist_obj in self.libformats.getAllMylistMyformat():
                self.log.write(u'%sの更新チェック' % mylist_obj.ID)
                self.various.rsscheck(mylist_obj)
                self.checkdiscontinue()

            """
            *DL対象を決定
            """
            for item in self.libformats.getAllMovieMyformat():
                if item.state == False:
                    dllist.append(item)
                else:  continue

            self.checkdiscontinue()

            """DL"""
            for movieobj in dllist:
                api = nicoAPI.Nicovideo(movie_id=movieobj.ID, mylist_id=movieobj.mylist_id)
                
                """情報登録"""
                # タイトル
                title = api.get_movie_title()
                self.log.write(title)
                self.st_title.SetLabel(title)
                self.libformats.rewrite(myformat=movieobj, factor='title', value=title)
                self.checkdiscontinue()  #
                #wx.PostEvent(self.parent, EVT_RELOADobj)  #
                """保存"""
                # 保存場所決定
                subfolder = os.path.join(os.getcwd(), self.SUBFOLDER)
                if not os.path.exists(subfolder):  os.mkdir(subfolder)
                savedir = self.infoobj.savedir
                if movieobj.mylist_id:
                    # マイリストが登録されていたら
                    mylisttitle = self.various.filenamecheck(self.libformats.getMylistMyformat(movieobj.mylist_id).title)
                    try:
                        savedir = os.path.join(savedir, mylisttitle)
                    except TypeError:
                        # マイリス名がう上手く保存されていなかった
                        self.various.reloadmylistdata(self.libformats.getMylistMyformat(movieobj.mylist_id))
                        try:
                            savedir = os.path.join(savedir, mylisttitle)
                        except TypeError:
                        # やり直してもだめだったら
                                savedir = self.infoobj.savedir
                if not os.path.exists(savedir):
                    # フォルダを作成
                    os.makedirs(savedir)
                """それぞれ一時フォルダに保存"""
                # 動画
                strage = api.get_storageURL(nicovideo_id=self.infoobj.nico_id, nicovideo_pw=self.infoobj.nico_pw)
                #   ログイン
                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
                req = urllib2.Request("https://secure.nicovideo.jp/secure/login")
                req.add_data(urllib.urlencode({"mail":self.infoobj.nico_id, "password":self.infoobj.nico_pw}))
                opener.open(req)
                opener.open("http://www.nicovideo.jp/watch/"+movieobj.ID)
                res = opener.open(strage)
                moviename = self.various.filenamecheck(movieobj.title+'.'+res.info().getsubtype())
                moviepath = os.path.join(subfolder, moviename)
                self.checkdiscontinue() ##
                #   動画サイズ取得
                if strage.find('low') == -1:  # 画質high
                    size = api.get_movie_size_high()
                elif strage.find('low') > -1:  # 画質low
                    size = api.get_movie_size_low()
                starttime = int(time.clock())
                spead = ptime = 0
                ff = open(moviepath, 'wb')
                try:
                    layout = False
                    while int(ff.tell()) < size:
                        self.checkdiscontinue()  ##
                        ff.write(res.read(self.BUFFERSIZE))
                        par = (float(ff.tell())/float(size))*100
                        runningtime = int(time.clock())- starttime
                        if runningtime > 0:
                            spead = int(ff.tell())/runningtime
                            ptime = (size-int(ff.tell()))/spead/60.0
                        else:  ptime = 0.00
                        if ptime >= 1:
                            self.st_time.SetLabel(u'残り%.2f分' % ptime)
                        elif 0 <= ptime < 1:
                            ptime *= 60.0
                            self.st_time.SetLabel(u'残り%.0f秒' % ptime)
                        self.frame.SetStatusText(u'%s/%s %.2f%%'%(ff.tell(), size, par))
                        if not layout:
                            self.Layout()
                            layout = True
                    del runningtime, spead, ptime
                    self.st_time.SetLabel(u'')
                finally:  ff.close()
                # サムネ
                thumbnailpath = api.save_thumbnail(subfolder, self.various.filenamecheck(movieobj.title))
                self.checkdiscontinue()  ##
                wx.PostEvent(self.parent, EVT_RELOADobj)  ##
                # コメント 
                commentpath = api.save_comment(self.infoobj.nico_id, self.infoobj.nico_pw, subfolder, self.various.filenamecheck(movieobj.title), fig=1000)
                self.checkdiscontinue()  ##
                wx.PostEvent(self.parent, EVT_RELOADobj)  ##
                # 説明
                description = api.get_movie_description()
                self.checkdiscontinue()  ##
                wx.PostEvent(self.parent, EVT_RELOADobj)  ##
                """保存フォルダに移動"""
                pathes = [moviepath, thumbnailpath, commentpath]
                count = 0
                for old in pathes:
                    _, name = os.path.split(old)
                    new = os.path.join(savedir, name)
                    if os.path.exists(new):
                        # 同名ファイルがあったら削除
                        os.remove(new)
                    os.rename(old, new)
                    pathes[count] = new
                    #self.log.write(u'移動(%s\n-> %s)' % (str(old), str(new))
                    count += 1
                moviepath, thumbnailpath, commentpath = pathes
                """情報の書き換え"""
                self.libformats.rewrite(myformat=movieobj, factor='path', value=moviepath)
                self.libformats.rewrite(myformat=movieobj, factor='thumbnail', value=thumbnailpath)
                self.libformats.rewrite(myformat=movieobj, factor='size', value=size)
                self.libformats.rewrite(myformat=movieobj, factor='description', value=description)
                self.libformats.rewrite(myformat=movieobj, factor='state', value=True)
                self.checkdiscontinue() ##
                """メール送信"""
                if self.cb.GetValue():
                    self.sendmail = Sendmail.nicodl_sendmail(self.infoobj.gmail_id, self.infoobj.gmail_pw, self.infoobj.toaddr)
                    self.sendmail.main("".join([title, "\n\n", description]), movieobj.ID)
            #time.sleep(WAITTIME)
            wx.PostEvent(self.parent, EVT_RELOADobj)  #
            self.running = False
            self.call()

        except DownloadDiscontinueException:
            return False
        except urllib2.URLError:
            self.log.write(u'エラーが発生しました。初めからやり直します。')
            self.call()

    def call(self):
        self.frame.SetStatusText('call')
        if self.running:
            self.log.write('Pass')
        else:
            self.st_title.SetLabel('')
            self.frame.SetStatusText('')
            self.frame.SetLabel('')
            th = threading.Thread(target=self.download)
            th.daemon = True
            th.start()
            self.btn.SetLabel('Stop')
            self.stop = False

    def chengestop(self):
        """
        self.stop フラグを変更
        """
        self.stop = not self.stop

        if not self.stop:
            self.call()

    def checkdiscontinue(self):
        """
        self.stop == Trueでエラー発生
        """
        if self.stop:
            self.log.write('Stop')
            self.running = False
            self.btn.SetLabel('Start')
            self.st_title.SetLabel('')
            self.frame.SetStatusText('')
            self.frame.SetLabel('')
            raise DownloadDiscontinueException

    def OnButton(self, evt):
        if not self.stop:
            self.frame.SetLabel(u'終了処理中...')
        self.chengestop()

    def SettingInfo(self, evt):
        dlg = InfoDialog(self, gmail_id=self.infoobj.gmail_id, gmail_pw=self.infoobj.gmail_pw,
                               nico_id=self.infoobj.nico_id, nico_pw=self.infoobj.nico_pw,
                               toaddr=self.infoobj.toaddr, savedir=self.infoobj.savedir)
        if dlg.ShowModal() == wx.ID_OK:
            infof = dlg.GetValues()
            self.infoobj.gmail_id = infof.gmail_id
            self.infoobj.gmail_pw = infof.gmail_pw
            self.infoobj.nico_id = infof.nico_id
            self.infoobj.nico_pw = infof.nico_pw
            self.infoobj.toaddr = infof.toaddr
            self.infoobj.savedir = infof.savedir
            self.infoobj.save()
            self.infoobj.load()
        else:  pass
        dlg.Destroy()

    """
    def calc(self, allsize, csize, ):
        
        runningtime = int(time.clock())- starttime
        if runningtime > 0:
            spead = int(ff.tell())/runningtime
            ptime = (size-int(ff.tell()))/spead/60.0
        else:  ptime = 0.00
        if ptime >= 1:
            self.st_time.SetLabel(u'残り%.2f分' % ptime)
        elif 0 <= ptime < 1:
            ptime *= 60.0
            self.st_time.SetLabel(u'残り%.0f秒' % ptime)
        self.frame.SetStatusText(u'%s/%s %.2f%%'%(ff.tell(), size, par))"""

class DownloadDiscontinueException(Exception):
    """
    DLを中止するときに発令
    """
    def __str__(self):                   # エラーメッセージ
        return 'DL was discontinued'

class InfoDialog(wx.Dialog):
    def __init__(self, parent, gmail_id, gmail_pw, nico_id, nico_pw, toaddr, savedir, *args, **kwargs):
        wx.Dialog.__init__(self, parent=parent, title=u'設定', *args, **kwargs)
        
        self.gmail_id = gmail_id
        self.gmail_pw = gmail_pw
        self.nico_id = nico_id
        self.nico_pw = nico_pw
        self.toaddr = toaddr
        self.savedir = savedir
        
        # Wigets
        self.gmail_id_st = wx.StaticText(self, label=u'Gmail ID           ')
        self.gmail_pw_st = wx.StaticText(self, label=u'Gmail PW         ')
        self.nico_id_st = wx.StaticText(self, label=u'ニコニコ動画 ID   ')
        self.nico_pw_st = wx.StaticText(self, label=u'ニコニコ動画 PW  ')
        self.toaddr_st = wx.StaticText(self, label=u'完了メール送信先')
        self.gmail_id_tc = wx.TextCtrl(self, value=self.gmail_id)
        self.gmail_pw_tc = wx.TextCtrl(self, value=self.gmail_pw, style=wx.TE_PASSWORD)
        self.nico_id_tc = wx.TextCtrl(self, value=self.nico_id)
        self.nico_pw_tc = wx.TextCtrl(self, value=self.nico_pw, style=wx.TE_PASSWORD)
        self.toaddr_tc = wx.TextCtrl(self, value=self.toaddr)
        self.dbb = filebrowse.DirBrowseButton(self, labelText=u'フォルダ選択', buttonText=u'参照', newDirectory=True)
        self.dbb.SetValue(self.savedir)
        
        sizer0 = wx.BoxSizer(wx.VERTICAL)
        sizer_0 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_0.Add(self.gmail_id_st, 0, wx.EXPAND)
        sizer_0.Add(self.gmail_id_tc, 1, wx.EXPAND)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(self.gmail_pw_st , 0, wx.EXPAND)
        sizer_1.Add(self.gmail_pw_tc , 1, wx.EXPAND)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.nico_id_st , 0, wx.EXPAND)
        sizer_2.Add(self.nico_id_tc , 1, wx.EXPAND)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(self.nico_pw_st , 0, wx.EXPAND)
        sizer_3.Add(self.nico_pw_tc , 1, wx.EXPAND)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(self.toaddr_st , 0, wx.EXPAND)
        sizer_4.Add(self.toaddr_tc , 1, wx.EXPAND)
        sizer0.Add(sizer_0, 0, wx.EXPAND|wx.TOP|wx.EAST|wx.WEST, 3)
        sizer0.Add(sizer_1, 0, wx.EXPAND|wx.TOP|wx.EAST|wx.WEST, 3)
        sizer0.Add(sizer_2, 0, wx.EXPAND|wx.TOP|wx.EAST|wx.WEST, 3)
        sizer0.Add(sizer_3, 0, wx.EXPAND|wx.TOP|wx.EAST|wx.WEST, 3)
        sizer0.Add(sizer_4, 0, wx.EXPAND|wx.TOP|wx.EAST|wx.WEST, 3)
        sizer0.Add(self.dbb, 0, wx.EXPAND|wx.TOP|wx.EAST|wx.WEST, 3)
        # line
        line = wx.StaticLine(self)
        sizer0.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
        # Dialog Button
        # OK
        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_OK, label=u'保存')
        btn.SetDefault()
        btnsizer.AddButton(btn)
        # CANCEL 
        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()
        sizer0.Add(btnsizer, 0, flag=wx.ALIGN_CENTER|wx.TOP|wx.DOWN, border=5)
        
        self.SetSizerAndFit(sizer0)

    def GetValues(self):
        infoformats = Formats.InfoFormats('.')
        return infoformats.mkCliantInfoFormat(gmail_id=self.gmail_id_tc.GetValue(),
                                              gmail_pw=self.gmail_pw_tc.GetValue(),
                                              nico_id=self.nico_id_tc.GetValue(),
                                              nico_pw=self.nico_pw_tc.GetValue(),
                                              toaddr=self.toaddr_tc.GetValue(),
                                              savedir=self.dbb.GetValue())


""" """
"""ListCtrlまとめ"""
class ListCtrlNotebook(wx.Notebook):
    def __init__(self, log, libraryfilepath, libraryfilename, *args, **kwargs):
        wx.Notebook.__init__(self, style=wx.BK_DEFAULT,*args, **kwargs)
        #self.log = log

        self.movie_lc = nicoDL_MovieListCtrl(log=log, libraryfilepath=libraryfilepath, libraryfilename=libraryfilename, parent=self)
        self.mylist_lc = nicoDL_MylistListCtrl(log=log, libraryfilepath=libraryfilepath, libraryfilename=libraryfilename, parent=self)
        
        self.AddPage(self.movie_lc, u'動画')
        self.AddPage(self.mylist_lc, u'マイリス')

    def load(self, evt):
        #print 'Reload'
        self.movie_lc.load()
        self.mylist_lc.load()
""" """

"""全体のまとめ"""
class nicoDL(wx.Panel):
    def __init__(self, log, libraryfilepath, libraryfilename, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        if kwargs.has_key('parent'):  self.parent = kwargs['parent']
        else:  self.parent = args[0]
        self.download_p = nicoDL_Download(log=log, libraryfilepath=libraryfilepath, libraryfilename=libraryfilename, parentframe=self.parent, parent=self)
        self.listctrl_nb = ListCtrlNotebook(log=log, libraryfilepath=libraryfilepath, libraryfilename=libraryfilename, parent=self)

        #self.log = log
        self.setmenu()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.download_p, 0, wx.EXPAND)
        sizer.Add(self.listctrl_nb, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer)
        
        self.Bind(EVT_RELOAD, self.listctrl_nb.load)
        
    def setmenu(self):
        # menu_menu
        menu_menu = wx.Menu()
        # menuItem_setting
        self.menuItem_reloadID = wx.NewId()
        menu_menu.Append(id=self.menuItem_reloadID, text=u'更新')
        self.menuItem_settingID = wx.NewId()
        menu_menu.Append(id=self.menuItem_settingID, text=u'設定')

        menuBar = self.parent.menuBar
        menuBar.Append(menu_menu, u'メニュー')
        self.parent.SetMenuBar(menuBar)
        
        self.parent.Bind(wx.EVT_MENU, self.download_p.SettingInfo, id=self.menuItem_settingID)
        self.parent.Bind(wx.EVT_MENU, self.listctrl_nb.load, id=self.menuItem_reloadID)

""" """


class MainWin(wx.Frame):
    def __init__(self, libraryfilepath, libraryfilename, *args, **kwargs):
        if os.path.exists('window.nco'):
            ff = open('window.nco')
            try:  data = pickle.load(ff)
            except:  data={'size':(100,100), 'pos':(0,0)}
            finally:  ff.close()
        else:  data={'size':(100,100), 'pos':(0,0)}

        wx.Frame.__init__(self, size=data['size'], pos=data['pos'], *args, **kwargs)
        self.CreateStatusBar()
        self.all = nicoDL(libraryfilepath=libraryfilepath, libraryfilename=libraryfilename, parent=self)
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, evt):
        size = self.GetSize()
        pos = self.GetPosition()
        
        ff = open('window.nco', 'w')
        try:
            pickle.dump({'size':size,
                         'pos':pos}, ff)
        finally:  ff.close()
        self.Destroy()


if __name__ == '__main__':
    #import wx.lib.inspection as inspectin
    os.chdir(r"C:\Users\KarasawaTakahiro\workspace\nicoWorld\src\tests")
    app = wx.App(redirect=False)
    win = MainWin(libraryfilepath=r'C:\Users\KarasawaTakahiro\workspace\nicoWorld\src\tests',
                  libraryfilename=LIBRARYFILENAME,
                  parent=None)
    win.Show()
    #inspectin.InspectionTool().Show()
    app.MainLoop()
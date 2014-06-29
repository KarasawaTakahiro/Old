
# coding: utf-8
"""
created on 2012/03/26 (since)
created by KarasawaTakahiro
"""

import cookielib
import modules.formats as Formats
import modules.nicodl_sendmail as Sendmail
import modules.nicodl_various as Various
import modules.nicovideoAPI as nicoAPI
import os
import skeltons.minelistctrl as MineListCtrl
import threading
import time
import urllib
import urllib2
import watchelper.watchelper_main as modWatchelper
import wx
import wx.lib.filebrowsebutton as filebrowse
import wx.lib.platebtn as platebtn
import wx.lib.scrolledpanel as scrolledpanel


_CDIR = os.getcwd()
_DATADIR = os.path.join(_CDIR, u'data')
_LIBRARYFILEPATH = _DATADIR
_LIBRARYFILENAME = u'Library.nco'
_INFOFILENAME = u'info.nco'
_WINSETTING = u'window.nco'
_BUFFERSIZE = 8 * 1024
_SUBFOLDER = u'temporary'
_WAITTIME = 3  ### second ###################
FORMATS = Formats.LibraryFormat(libraryfilepath=_LIBRARYFILEPATH, libraryfilename=_LIBRARYFILENAME)
FORMATS.load()
INFO = Formats.InfoFormats(_DATADIR, _INFOFILENAME)
INFO.load()

print _LIBRARYFILEPATH

class Welcome(wx.Panel):
    def __init__(self, log, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        self.log = log
        
        wx.StaticText(self, label=u'Welcome')
        
        self.log.write('Welcome!!')

#-- nicoDL ----------------------------------------------------------------
#-- イベント定義  --------------------------------------------------
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


class EVT_FinishDL(wx.PyCommandEvent):
    """
    """
    def __init__(self, etype, eid):
        wx.PyCommandEvent.__init__(self, etype, eid)

        self.movie_id = None
        self.mylist_id = None
        self.movie_path = None
        self.thumbnail = None
        self.size = None
        self.description = None
        self.state = None

    def clear(self):
        self.movie_id = None
        self.mylist_id = None
        self.movie_path = None
        self.thumbnail = None
        self.size = None
        self.description = None
        self.state = None


EVT_TYPE_FINISHDL = wx.NewEventType()
EVT_FINISHDL = wx.PyEventBinder(EVT_TYPE_FINISHDL)
EVT_FINISHDLobj = EVT_FinishDL(EVT_TYPE_FINISHDL, wx.ID_ANY)


class EVT_HitMovie(wx.PyCommandEvent):
    u"""
    *動画がヒット
    *リストに反映させるためのイベント
    """
    def __init__(self, etype, eid):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.MovieMyformat = None

    def Clear(self):
        self.MovieMyformat = None

EVT_TYPE_HITMOVIE = wx.NewEventType()
EVT_HITMOVIE = wx.PyEventBinder(EVT_TYPE_HITMOVIE)
EVT_HITMOVIEobj = EVT_HitMovie(EVT_TYPE_HITMOVIE, wx.ID_ANY)

#-- ListCtrl ----------------------------------------
class MovieListCtrl(MineListCtrl.MySortListCtrl):
    def __init__(self, log, parent):
        MineListCtrl.MySortListCtrl.__init__(self, parent=parent)
        self.selected_index = None
        self.selected_movie_id = None
        self.DataMap = {}

        self.log = log
        self.parent = parent

        self.loaddata()

        self.InsertColumn(0,u'動画ID')
        self.InsertColumn(1, u'タイトル')
        self.InsertColumn(2, u'DL')
        self.InsertColumn(3, u'説明')
        self.InsertColumn(4, u'マイリス')
        self.Load()
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(3, 500)
        self.SetColumnWidth(4, wx.LIST_AUTOSIZE)

        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelected)
        self.Bind(EVT_RELOAD, self.reset)
        self.Bind(EVT_FINISHDL, self.rewrite)
        self.Bind(EVT_HITMOVIE, self.appenddata)

    def loaddata(self):
        self.DataMap = {}
        count = 0
        for movief in FORMATS.getAllMovieMyformat():
            self.DataMap.update({count:[movief.ID, movief.title, movief.state, movief.description, movief.mylist_id]})
            count += 1

    def appenddata(self, evt):
        """
        *リストとDataMapに追加していく
        """
        #print 'appendData'
        movieformat = evt.MovieMyformat
        index = self.GetItemCount()
        self.DataMap.update({index:[movieformat.ID, movieformat.title, movieformat.state, movieformat.description, movieformat.mylist_id]})
        value = self.DataMap[index]
        dist = self.InsertStringItem(index, value[0])
        self.SetStringItem(dist, 1, value[1])
        self.SetStringItem(dist, 2, str(value[2]))
        if not value[3]:  self.SetStringItem(dist, 3, '')
        else:  self.SetStringItem(dist, 3, value[3][:50])
        self.SetStringItem(dist, 4, str(value[4]))
        self.SetItemData(index, index)
        evt.Clear()

    def reset(self, evt):
        self.loaddata()
        self.DeleteAllItems()
        self.Load()

    def OnSelected(self, evt):
        self.selected_index = evt.GetIndex()
        self.selected_movie_id = evt.GetText()

    def rewrite(self, col, value, mess=False, movie_id=False, index=False):
        """
        col: self.load()を参照して選択
        value: 変更する値
        
        movie_idが与えられない場合self.selected_movie_idに対して処理をする
        indexが与えられない場合self.selectedindexに対して処理をする
        """
        #print 'MovieListCtrl Rewrite'
        #print 'selected index:', self.selected_index
        #print 'index:', index
        if (not self.selected_movie_id) and (not movie_id):
            return 
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
        if (index or index==0) and not(index==False):
            self.SetStringItem(index=index, col=col, label=unicode(value))
        else:
            self.SetStringItem(index=self.selected_index, col=col, label=unicode(value))
        if movie_id:
            FORMATS.rewrite(myformat=FORMATS.getMovieMyformat(movie_id), factor=factor, value=value)
        else:
            FORMATS.rewrite(myformat=FORMATS.getMovieMyformat(self.selected_movie_id), factor=factor, value=value)
        if mess:
            if movie_id:
                self.log.write_1(movie_id, mess)
            else:
                self.log.write_1(self.selected_movie_id, mess)

    """右クリックメニュー"""
    def OnRightClick(self, evt):
        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            self.popupID3 = wx.NewId()
            self.popupID4 = wx.NewId()
            #self.popupID5 = wx.NewId()
            #self.popupID6 = wx.NewId()

            self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
            self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
            self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
            self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
            #self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
            #self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)

        # make a menu
        menu = wx.Menu()
        # add some items
        menu.Append(self.popupID1, u"リセット")
        menu.Append(self.popupID4, u"DL済み")
        menu.Append(self.popupID2, u"更新")
        menu.Append(self.popupID3, u"削除")
        #menu.Append(self.popupID5, "GetItem")
        #menu.Append(self.popupID6, "Edit")

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu)
        menu.Destroy()

    def OnPopupOne(self, evt):
        """リセット"""
        self.rewrite(col='state', value=False, mess=u'DL済みをリセット')

    def OnPopupTwo(self, evt):
        """タイトルと情報を更新"""
        try:
            api = nicoAPI.Nicovideo(movie_id=self.selected_movie_id)
            title = api.get_movie_title()
            description = api.get_movie_description()
        except urllib2.URLError:
            self.log.write_info(u'ニコニコ動画に接続できません')
            return
        myformat = FORMATS.getMovieMyformat(movie_id=self.selected_movie_id)
        FORMATS.rewrite(myformat, factor='title', value=title)
        self.log.write_1(myformat.ID, u'タイトルを更新')
        FORMATS.rewrite(myformat, factor='description', value=description)
        self.log.write_1(myformat.ID, u'説明を更新')

    def OnPopupThree(self, evt):
        """削除"""
        movieobj = FORMATS.getMovieMyformat(self.selected_movie_id)
        if FORMATS.remove(movieobj):
            self.log.write(u'%sを削除しました'%movieobj.ID)
            #wx.PostEvent(self.parent.parent, EVT_RELOADobj)
            self.DeleteItem(self.selected_index)
            # DataMapを整理 
            self.reset(None)
        else:
            self.log.write_info(u'%sの削除に失敗しました'%movieobj.ID)    
    def OnPopupFour(self, evt):
        """DL済みとしてマーク"""
        self.rewrite(col='state', value=True, mess=u'DL済みとしてマーク')

# オーバーライド
    def Load(self):
        index = self.GetItemCount()
        for key, value in self.DataMap.items():
            #print index, value
            dist = self.InsertStringItem(index, value[0])
            self.SetStringItem(dist, 1, value[1])
            self.SetStringItem(dist, 2, str(value[2]))
            if not value[3]:  self.SetStringItem(dist, 3, '')
            else:  self.SetStringItem(dist, 3, value[3][:50])
            self.SetStringItem(dist, 4, str(value[4]))
            self.SetItemData(index, key)
            index += 1

    def AscendingCmp(self, col):
        #printu'昇順'
        li = []
        for value in self.DataMap.itervalues():
            li.append(value)
        if col == 0:
            li.sort(cmp=self.movieIDcmp)
        elif col == 2:
            li.sort(cmp=self.Boolcmp)
        elif col == 4:
            li.sort(cmp=self.mylistIDcmp)
        else:
            li.sort()
        index = 0
        itemMap = {}
        for item in li:
            itemMap.update({index:item})
            index += 1
        self.DataMap =  itemMap

    def DescendingCmp(self, col):
        #printu'降順'
        li = []
        for value in self.DataMap.itervalues():
            li.append(value)
        if col == 0:
            li.sort(cmp=self.movieIDcmp)
        elif col == 2:
            li.sort(cmp=self.Boolcmp)
        elif col == 4:
            li.sort(cmp=self.mylistIDcmp)
        else:
            li.sort(cmp=self.stdcmp)
        li.reverse()
        index = 0
        itemMap = {}
        for item in li:
            itemMap.update({index:item})
            index += 1
        self.DataMap =  itemMap

    def movieIDcmp(self, item1, item2):
        return cmp(int(item1[0][2:]), int(item2[0][2:]))
    def mylistIDcmp(self, item1, item2):
        #print 'item1:', item1
        #print 'item2:', item2
        """itemはintかFalse"""
        if not item1[4]:
            # item1[3] == False
            return 1
        elif not item2[4]:
            # item2[3] == False
            return -1
        elif (not item1[4]) and (not item2[4]):
            # item1[3] == item2[3] == False
            return 0
        else:
            # item1[3] == item2[3] == int
            return cmp(int(item1[4]), int(item2[4]))
    def Boolcmp(self, item1, item2):
        """True > False"""
        if item1:
            if item2:  return 0
            else:  return 1
        else:
            if item2:  return -1
            else:  return 0
    def stdcmp(self, item1, item2):
        return cmp(item1[self._SelectedCol], item2[self._SelectedCol])

class MylistListCtrl(MineListCtrl.MySortListCtrl):
    def __init__(self, log, parent):
        MineListCtrl.MySortListCtrl.__init__(self, parent=parent)

        self.selected_index = None
        self.selected_mylist_id = None
        self.DataMap = {}

        self.log = log
        self.parent = parent
        self.loaddata()
        self.InsertColumn(0, u'ID')
        self.InsertColumn(1, u'タイトル')
        self.InsertColumn(2, u'RSS')
        self.InsertColumn(3, u'説明')
        self.Load()
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(3, 500)

        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)
        self.Bind(EVT_RELOAD, self.reset)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelected)

    def OnSelected(self, evt):
        self.selected_index = evt.GetIndex()
        self.selected_mylist_id = evt.GetText()

    def loaddata(self):
        self.DataMap = {}
        no = 0
        for item in FORMATS.getAllMylistMyformat():
            self.DataMap.update({no:[item.ID, item.title, str(item.rss), item.description]})
            no += 1

    def reset(self, evt):
        self.loaddata()
        self.DeleteAllItems()
        self.Load()

    def rewrite(self, col, value, mess=False):
        """
        col: self.load()を参照して選択
        value: 変更する値
        """
        if (col == 2) or (col == 'rss'):
            factor = 'rss'
            col = 2
        else:  raise ValueError, u'myformatとの該当なし'
        self.SetStringItem(index=self.selected_index, col=col, label=unicode(value))
        FORMATS.rewrite(myformat=FORMATS.getMylistMyformat(self.selected_mylist_id), factor=factor, value=value)
        if mess:
            self.log.write_1(self.selected_mylist_id, mess)

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
        menu.Append(self.popupID1, u"RSS変更")
        menu.Append(self.popupID2, u"リセット")
        menu.Append(self.popupID3, u"削除")
        #menu.Append(self.popupID4, "DeleteAllItems")
        #menu.Append(self.popupID5, "GetItem")
        #menu.Append(self.popupID6, "Edit")

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu)
        menu.Destroy()

    def OnPopupOne(self, evt):
        """RSS変更"""
        mylistobj = FORMATS.getMylistMyformat(self.selected_mylist_id)
        rss = not mylistobj.rss
        self.rewrite(col='rss', value=rss, mess=u'RSSを変更')

    def OnPopupTwo(self, evt):
        """リセット"""
        mylistobj = FORMATS.getMylistMyformat(self.selected_mylist_id)
        for moID in mylistobj.catalog:
            self.log.write(u'%sのDL済みをリセット'%moID)
        FORMATS.reset(mylistobj)
        wx.PostEvent(self.parent.parent, EVT_RELOADobj)  ## 後々

    def OnPopupThree(self, evt):
        mylistobj = FORMATS.getMylistMyformat(self.selected_mylist_id)
        if FORMATS.remove(mylistobj):
            self.log.write(u'%sを削除'%mylistobj.ID)
            self.DeleteItem(self.selected_index)
            self.reset(None)
        else:
            self.log.write_info(u'%sの削除に失敗しました'%mylistobj.ID)
        self.log.write(u'OnPopupThree')
    """ """
    """ オーバーライド"""
    def Load(self):
        index = self.GetItemCount()
        for key, value in self.DataMap.items():
            #print index, value
            dist = self.InsertStringItem(index, value[0])
            self.SetStringItem(dist, 1, value[1])
            self.SetStringItem(dist, 2, str(value[2]))
            self.SetStringItem(dist, 3, value[3][:50])
            self.SetItemData(index, key)
            index += 1

    def AscendingCmp(self, col):
        #print u'昇順'
        li = []
        for value in self.DataMap.itervalues():
            li.append(value)
        if col == 0:
            li.sort(cmp=self.IDcmp)
        elif col == 2:
            li.sort(cmp=self.Boolcmp)
        else:
            li.sort()
        index = 0
        itemMap = {}
        for item in li:
            itemMap.update({index:item})
            index += 1
        self.DataMap =  itemMap

    def DescendingCmp(self, col):
        #print u'降順'
        li = []
        for value in self.DataMap.itervalues():
            li.append(value)
        if col == 0:
            li.sort(cmp=self.IDcmp)
        elif col == 2:
            li.sort(cmp=self.Boolcmp)
        else:
            li.sort(cmp=self.stdcmp)
        li.reverse()
        index = 0
        itemMap = {}
        for item in li:
            itemMap.update({index:item})
            index += 1
        self.DataMap =  itemMap
    
    def IDcmp(self, item1, item2):
        return cmp(int(item1[self.SelectedCol]), int(item2[self.SelectedCol]))
    def Boolcmp(self, item1, item2):
        """True > False"""
        if item1:
            if item2:  return 0
            else:  return 1
        else:
            if item2:  return -1
            else:  return 0
    def stdcmp(self, item1, item2):
        return cmp(item1[self.SelectedCol], item2[self.SelectedCol])


#-- ListCtrlまとめ  ------------------------------------
class ListCtrlNotebook(wx.Notebook):
    def __init__(self, log, *args, **kwargs):
        wx.Notebook.__init__(self, style=wx.BK_DEFAULT, *args, **kwargs)
        if kwargs.has_key('parent'):  self.parent = kwargs['parent']
        else:  self.parent = args[0]
        #self.log = log

        self.movie_lc = MovieListCtrl(log=log, parent=self)
        self.mylist_lc = MylistListCtrl(log=log, parent=self)
        
        self.AddPage(self.movie_lc, u'動画')
        self.AddPage(self.mylist_lc, u'マイリス')
        
        self.Bind(EVT_FINISHDL, self.rewrite)

    def load(self, evt):
        #print'Reload'
        try:
            wx.PostEvent(self.movie_lc, EVT_RELOADobj)
        except EOFError:
            time.sleep(5)
            wx.PostEvent(self.movie_lc, EVT_RELOADobj)
        try:
            wx.PostEvent(self.mylist_lc, EVT_RELOADobj)
        except EOFError:
            time.sleep(5)
            wx.PostEvent(self.mylist_lc, EVT_RELOADobj)

    def rewrite(self, evt):
        """
        """
        #print 'Rewrite'
        #print 'movie:', evt.movie_id
        #print 'state:', evt.state
        index = -1
        for key, value in self.movie_lc.DataMap.items():
            if value[0] == evt.movie_id:
                index = key
                break
            else:  continue
        else: 
            if index == -1:
                evt.clear()
                return
        movie_id = evt.movie_id
        if evt.state:
            self.movie_lc.rewrite(col='state', value=evt.state, movie_id=movie_id, index=index)
        if evt.description:
            self.movie_lc.rewrite(col='description', value=evt.description, movie_id=movie_id, index=index)
        if evt.mylist_id:
            self.movie_lc.rewrite(col='mylist_id', value=evt.mylist_id, movie_id=movie_id, index=index)
        evt.clear()

#-- Download ------------------------------------
class nicoDL_Download(wx.Panel):
    def __init__(self, log, parentframe, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        if kwargs.has_key('parent'):  self.parent = kwargs['parent']
        else:  self.parent = args[0]
        self.running = False
        self.stop = False

        #
        self.various = Various.nicoDL_Various(log=log, libraryfilepath=_LIBRARYFILEPATH, libraryfilename=_LIBRARYFILENAME)
        FORMATS.load()
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

    def movieIDcmp(self, item1, item2):
        return cmp(int(item1.ID[2:]), int(item2.ID[2:]))

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
                myformat = self.various.geturl(INFO.gmail_id, INFO.gmail_pw)
            except:
                self.log.write(u'Gmailにログインできませんでした。')
                self.stop = True
                try:  self.checkdiscontinue()
                except:  return False
            if myformat:
                FORMATS.append(myformat)
                if myformat.type == 'MYLIST':
                    self.various.reloadmylistdata(myformat)
                elif myformat.type == 'MOVIE':
                    self.various.reloadmoviedata(myformat)
                    EVT_HITMOVIEobj.MovieMyformat = myformat
                    wx.PostEvent(self.parent, EVT_HITMOVIEobj)
            else:  self.log.write(u'新規データはありませんでした。')

            self.checkdiscontinue()

            api = nicoAPI.Nicovideo()
            login = api.logintest(ID=INFO.nico_id, PW=INFO.nico_pw)
            if not login:
                self.log.write(u'ニコニコ動画にログインできませんでした。')
                self.stop = True
                self.checkdiscontinue()

            """
            RSSチェック
            *ライブラリ登録
            """
            for mylist_obj in FORMATS.getAllMylistMyformat():
                if mylist_obj.rss:
                    self.log.write(u'RSS: %s' % mylist_obj.ID)
                    try:
                        appended = self.various.rsscheck(mylist_obj)
                        if type(appended) != bool:
                            for item in appended:
                                EVT_HITMOVIEobj.MovieMyformat = item
                                wx.PostEvent(self.parent, EVT_HITMOVIEobj)
                    except EOFError:  pass
                self.checkdiscontinue()
                continue

            """
            *DL対象を決定
            """
            for item in FORMATS.getAllMovieMyformat():
                if item.state == False:
                    dllist.append(item)
                else:  continue

            dllist.sort(cmp=self.movieIDcmp)

            self.checkdiscontinue()

            """DL"""
            for movieobj in dllist:
                api = nicoAPI.Nicovideo(movie_id=movieobj.ID, mylist_id=movieobj.mylist_id)
                
                """情報登録"""
                # タイトル
                title = api.get_movie_title()
                self.log.write_1(movieobj.ID, title)
                self.st_title.SetLabel(title)
                FORMATS.rewrite(myformat=movieobj, factor='title', value=title)
                self.checkdiscontinue()  #
                """保存"""
                # 保存場所決定
                subfolder = os.path.join(_CDIR, _SUBFOLDER)
                if not os.path.exists(subfolder):  os.mkdir(subfolder)
                savedir = INFO.savedir
                if movieobj.mylist_id:
                    # マイリストが登録されていたら
                    mylisttitle = self.various.filenamecheck(FORMATS.getMylistMyformat(movieobj.mylist_id).title)
                    try:
                        savedir = os.path.join(savedir, mylisttitle)
                    except TypeError:
                        # マイリス名がう上手く保存されていなかった
                        self.various.reloadmylistdata(FORMATS.getMylistMyformat(movieobj.mylist_id))
                        try:
                            savedir = os.path.join(savedir, mylisttitle)
                        except TypeError:
                        # やり直してもだめだったら
                                savedir = INFO.savedir
                if not os.path.exists(savedir):
                    # フォルダを作成
                    os.makedirs(savedir)
                """それぞれ一時フォルダに保存"""
                # 動画
                strage = api.get_storageURL(nicovideo_id=INFO.nico_id, nicovideo_pw=INFO.nico_pw)
                #   ログイン
                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
                req = urllib2.Request("https://secure.nicovideo.jp/secure/login")
                req.add_data(urllib.urlencode({"mail":INFO.nico_id, "password":INFO.nico_pw}))
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
                        ff.write(res.read(_BUFFERSIZE))
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
                # コメント 
                commentpath = api.save_comment(INFO.nico_id, INFO.nico_pw, subfolder, self.various.filenamecheck(movieobj.title), fig=1000)
                self.checkdiscontinue()  ##
                # 説明
                description = api.get_movie_description()
                self.checkdiscontinue()  ##
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
                FORMATS.rewrite(myformat=movieobj, factor='path', value=moviepath)
                FORMATS.rewrite(myformat=movieobj, factor='thumbnail', value=thumbnailpath)
                FORMATS.rewrite(myformat=movieobj, factor='size', value=size)
                FORMATS.rewrite(myformat=movieobj, factor='description', value=description)
                FORMATS.rewrite(myformat=movieobj, factor='state', value=True)
                EVT_FINISHDLobj.movie_id = movieobj.ID
                EVT_FINISHDLobj.mylist_id = movieobj.mylist_id
                EVT_FINISHDLobj.path = movieobj.path
                EVT_FINISHDLobj.thumbnail = movieobj.thumbnail
                EVT_FINISHDLobj.size = movieobj.size
                EVT_FINISHDLobj.description = movieobj.description
                EVT_FINISHDLobj.state = movieobj.state
                wx.PostEvent(self.parent, EVT_FINISHDLobj)  ##
                #wx.PostEvent(self.parent, EVT_RELOADobj)  ##
                self.checkdiscontinue() ##
                """メール送信"""
                if self.cb.GetValue():
                    self.sendmail = Sendmail.nicodl_sendmail(INFO.gmail_id, INFO.gmail_pw, INFO.toaddr)
                    self.sendmail.main("".join([title, "\n\n", description]), movieobj.ID)
            time.sleep(_WAITTIME)
            wx.PostEvent(self.parent, EVT_RELOADobj)  #
            self.running = False
            self.call()

        except DownloadDiscontinueException:
            return False
        except urllib2.URLError:
            self.log.write(u'エラーが発生しました。初めからやり直します。')
            self.running = False
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
        dlg = InfoDialog(self, gmail_id=INFO.gmail_id, gmail_pw=INFO.gmail_pw,
                               nico_id=INFO.nico_id, nico_pw=INFO.nico_pw,
                               toaddr=INFO.toaddr, savedir=INFO.savedir)
        if dlg.ShowModal() == wx.ID_OK:
            infof = dlg.GetValues()
            INFO.gmail_id = infof.gmail_id
            INFO.gmail_pw = infof.gmail_pw
            INFO.nico_id = infof.nico_id
            INFO.nico_pw = infof.nico_pw
            INFO.toaddr = infof.toaddr
            INFO.savedir = infof.savedir
            INFO.save()
            INFO.load()
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
    def __str__(self):
        # エラーメッセージ
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

#-- DL部まとめ ----------------------------------------
class nicoDL(wx.Panel):
    def __init__(self, log, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        if kwargs.has_key('parent'):  self.parent = kwargs['parent']
        else:  self.parent = args[0]
        self.download_p = nicoDL_Download(log=log, parentframe=self.parent, parent=self)
        self.listctrl_nb = ListCtrlNotebook(log=log, parent=self)

        #self.log = log
        self.setmenu()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.download_p, 0, wx.EXPAND)
        sizer.Add(self.listctrl_nb, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer)
        
        #self.Bind(EVT_RELOAD, self.listctrl_nb.load)
        self.Bind(EVT_FINISHDL, self.OnFinish)
        self.Bind(EVT_HITMOVIE, self.listctrl_nb.movie_lc.appenddata)

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

    def OnFinish(self, evt):
        wx.PostEvent(self.listctrl_nb, EVT_FINISHDLobj)


#--- LogWindow----------------------------------------------------------------
class LogWin(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        panel = wx.Panel(self)
        self.log_tc = wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.log_tc, 1, wx.EXPAND)
        panel.SetSizerAndFit(sizer)
        self.Layout()
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def write(self, string):
        """string"""
        self.log_tc.SetInsertionPointEnd()
        self.log_tc.WriteText(string)
        self.log_tc.WriteText('\n')
        
    def write_info(self, string):
        """! string !"""
        string = u'! %s !' % string
        self.write(string)

    def write_1(self, fstring, lstring):
        """[fstring] lstring"""
        string = u'[%s] %s' % (fstring, lstring)
        self.write(string)

    def show(self):
        self.Show()
    def hide(self):
        self.Hide()

    def OnClose(self, evt):
        self.hide()

#--- MainWindow ----------------------------------------------------------------
class MainWin(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.log = LogWin(parent=self, size=(300,200))
        self.CreateStatusBar()
        self.menuBar = wx.MenuBar()

        self.setmenu()
        self.log.Show()

        """ICON"""
        self.tb_ico = wx.TaskBarIcon()
        self.ico_32x32 = wx.Icon(os.path.join(_CDIR, "data\\32x32.ico"), wx.BITMAP_TYPE_ICO)
        self.tb_ico.SetIcon(self.ico_32x32, u"Hello")
        self.tb_ico.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.OnTBIcon)

        """SideMenu"""
        self.sidemenupanel = scrolledpanel.ScrolledPanel(self, size=(120, -1))
        self.side_welcome_btn = platebtn.PlateButton(self.sidemenupanel, label=u'Welcome', style=platebtn.PB_STYLE_GRADIENT)
        self.side_nicodl_btn = platebtn.PlateButton(self.sidemenupanel, label=u'nicodl_btn', style=platebtn.PB_STYLE_GRADIENT)
        self.side_watchelper_btn = platebtn.PlateButton(self.sidemenupanel, label=u'watchelper_btn', style=platebtn.PB_STYLE_GRADIENT)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.side_welcome_btn, 0, wx.EXPAND)
        sizer.Add(self.side_nicodl_btn, 0, wx.EXPAND)
        sizer.Add(self.side_watchelper_btn, 0, wx.EXPAND)
        self.sidemenupanel.SetSizer(sizer)
        self.sidemenupanel.SetAutoLayout(1)
        self.sidemenupanel.SetupScrolling()
        """ """
        """MainPanel"""
        # 以下にpanelを追加
        self.welcome_panel = Welcome(parent=self, log=self.log)
        self.nicodl_panel = nicoDL(parent=self, log=self.log)
        self.watchelper = modWatchelper.Watchelper(parent=self, log=self.log, path='c:\\Users\\Dev\\Desktop', name='watchelper.nco')
        # このリストに追加したパネルを追加
        self.paneles = [self.welcome_panel, self.nicodl_panel, self.watchelper]
        self.mainpanel = self.welcome_panel
        for item in self.paneles:
            if item == self.mainpanel:
                continue
            item.Hide()
        
        # sizer
        self.mainpanelsizer = wx.BoxSizer(wx.VERTICAL)
        self.mainpanelsizer.Add(self.mainpanel, 1, wx.EXPAND)
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.sidemenupanel, 0, wx.EXPAND)
        sizer1.Add(self.mainpanelsizer, 1, wx.EXPAND)
        self.SetSizer(sizer1)
        self.Layout()
        
        # Bind
        # ここにバインド
        self.Bind(wx.EVT_BUTTON, self.OnSideWelcomeButton, self.side_welcome_btn)
        self.Bind(wx.EVT_BUTTON, self.OnSidenicoDLButton, self.side_nicodl_btn)
        self.Bind(wx.EVT_BUTTON, self.OnSideWatchelperButton, self.side_watchelper_btn)
        """ """

        """サイドバーのボタンを押したとき
        --以下ひな形--
        self.oldmainpanel = self.mainpanel
        self.mainpanel = self.**追加したパネル**
        self.panel_layout()
        """

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def setmenu(self):
        # menu_menu
        menu_menu = wx.Menu()
        # menuItem_setting
        self.menuItem_showlog = wx.NewId()
        menu_menu.Append(id=self.menuItem_showlog, text=u'ログ表示')
        self.menuItem_hidelog = wx.NewId()
        menu_menu.Append(id=self.menuItem_hidelog, text=u'ログ隠す')

        self.menuBar.Append(menu_menu, u'ログウィンドウ')
        self.SetMenuBar(self.menuBar)
        
        self.Bind(wx.EVT_MENU, self.OnLogWinShow, id=self.menuItem_showlog)
        self.Bind(wx.EVT_MENU, self.OnLogWinHide, id=self.menuItem_hidelog)
        
    def OnLogWinShow(self, evt):
        self.log.show()
        self.log.SetFocus()
    def OnLogWinHide(self, evt):
        self.log.hide()

    def OnSideWelcomeButton(self, evt):
        self.oldmainpanel = self.mainpanel
        self.mainpanel = self.welcome_panel
        self.panel_layout()

    def OnSidenicoDLButton(self, evt):
        self.oldmainpanel = self.mainpanel
        self.mainpanel = self.nicodl_panel
        self.panel_layout()

    def OnSideWatchelperButton(self, evt):
        self.oldmainpanel = self.mainpanel
        self.mainpanel = self.watchelper
        self.panel_layout()

    def panel_layout(self):
        #print self.oldmainpanel
        #print self.mainpanel
        #print
        self.mainpanelsizer.Remove(self.oldmainpanel)
        self.mainpanelsizer.Add(self.mainpanel, 1, wx.EXPAND)
        for item in self.paneles:
            if item == self.mainpanel:
                item.Show()
            else:
                item.Hide()
        self.Layout()

    def OnClose(self, evt):
        self.Hide()

    """Task Bar"""
    def OnTBIcon(self, evt):
        if not hasattr(self, "popupID1"):  # 起動後、一度だけ定義する。
            self.tb_popupID1 = wx.NewId()
            self.tb_ico.Bind(wx.EVT_MENU, self.OnTBPopupOne, id=self.tb_popupID1) # Bind 先が icon なのがミソ
            self.tb_popupID2 = wx.NewId()
            self.tb_ico.Bind(wx.EVT_MENU, self.OnTBPopupTwo, id=self.tb_popupID2)
            #self.tb_popupID3 = wx.NewId()
            #self.tb_ico.Bind(wx.EVT_MENU, self.OnTBPopupThree, id=self.tb_popupID3)
        # メニュー作成
        menu = wx.Menu()
        menu.Append(self.tb_popupID1, u"ウィンドウを表示")
        menu.AppendSeparator()
        menu.Append(self.tb_popupID2, u"終了")

        self.tb_ico.PopupMenu(menu)
        menu.Destroy()

    def OnTBPopupOne(self, evt):
        """ウィンドウを表示"""
        self.Show()
        self.SetFocus()
        
    def AppClose(self, evt):
        self.tb_ico.Destroy()
        self.Destroy()

    def OnTBPopupTwo(self, evt):
        """終了"""
        self.AppClose(evt=None)

""" """

#-- main ----------------------------------------------

def main():
    app = wx.App(redirect=False)

    if not os.path.exists(_DATADIR):
        try:
            os.mkdir(_DATADIR)
        except:
            print u'raise error'
            return False

    win = MainWin(parent=None,
                  size=(800,350)
                  )
    win.Show()
    app.MainLoop()
    
if __name__ == '__main__':
    main()

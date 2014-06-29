
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
        self.log_tc.SetInsertionPointEnd()
        self.log_tc.WriteText(string)
        self.log_tc.WriteText('\n')
        
    def write_info(self, string):
        string = u'! %s !' % string
        self.write(string)

    def write_1(self, fstring, lstring):
        string = u'[%s] %s' % (fstring, lstring)
        self.write(string)

    def show(self):
        self.Show()
    def hide(self):
        self.Hide()

    def OnClose(self, evt):
        self.hide()



"""ListCtrl"""
class MovieListCtrl(wx.ListCtrl):
    def __init__(self, libraryfilepath, libraryfilename, parent, style=wx.WANTS_CHARS):
        wx.ListCtrl.__init__(self, parent=parent, style=wx.LC_REPORT
                                             | wx.BORDER_NONE
                                             | wx.LC_EDIT_LABELS
                                             | wx.LC_SORT_ASCENDING
                                             | wx.WANTS_CHARS)
        self.libraryfilepath = libraryfilepath
        self.libraryfilename = libraryfilename
        self.formats = Formats.LibraryFormat(libraryfilepath=libraryfilepath, libraryfilename=libraryfilename)
        self.selected = None

        self.load()

        # for wxMSW
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)
        self.Bind(EVT_RELOAD, self.load)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelected)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)
        
    def OnColClick(self, evt):
        pass


    def load(self):
        self.DeleteAllColumns()
        self.DeleteAllItems()
        self.InsertColumn(0, u'ID')
        self.InsertColumn(1, u'タイトル')
        self.InsertColumn(2, u'DL')
        self.InsertColumn(3, u'説明')
        self.InsertColumn(4, u'マイリスト')
        self.itemDataMap = {}
        
        data = self.formats.getAllMovieMyformat()
        no = 0
        for item in data:
            self.itemDataMap.update({no:(item.ID, item.title, str(item.state), item.description, item.mylist_id)})
            no += 1
        index = self.GetItemCount()
        for key, value in self.itemDataMap.items():
            dist = self.InsertStringItem(index, value[0])
            try:
                self.SetStringItem(dist, 1, value[1])
                self.SetStringItem(dist, 2, value[2])
                self.SetStringItem(dist, 3, value[3][0:50])
                self.SetStringItem(dist, 4, value[4])
                self.SetItemData(index, key)
            except TypeError:
                self.SetStringItem(dist, 1, str(value[1]))
                self.SetStringItem(dist, 2, str(value[2]))
                self.SetStringItem(dist, 3, str(value[3])[0:50])
                self.SetStringItem(dist, 4, str(value[4]))
                self.SetItemData(index, key)
            index += 1
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(3, 500)
        self.SetColumnWidth(4, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(5, wx.LIST_AUTOSIZE)

    def OnSelected(self, evt):
        self.selected = evt.GetIndex()

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
        self.SetStringItem(index=self.selected, col=col, label=unicode(value))
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

class nicoDL_MylistListCtrl(wx.Panel, listmix.ColumnSorterMixin):
    def __init__(self, libraryfilepath, libraryfilename, parent, style=wx.WANTS_CHARS):
        wx.Panel.__init__(self, parent=parent, style=style)

        self.formats = Formats.LibraryFormat(libraryfilepath=libraryfilepath, libraryfilename=libraryfilename)

        self.imli = wx.ImageList(16, 16)
        self.sm_up = self.imli.Add(images.SmallUpArrow.GetBitmap())
        self.sm_dn = self.imli.Add(images.SmallDnArrow.GetBitmap())
        self.load()
        listmix.ColumnSorterMixin.__init__(self, 5)
        # for wxMSW
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)
        self.Bind(EVT_RELOAD, self.load)


    def load(self):
        self.DeleteAllColumns()
        self.DeleteAllItems()

        self.InsertColumn(0, u'ID')
        self.InsertColumn(1, u'タイトル')
        self.InsertColumn(2, u'RSS')
        self.InsertColumn(3, u'説明')
        self.itemDataMap = {}

        no = 0
        for item in self.formats.getAllMylistMyformat():
            self.itemDataMap.update({no:(item.ID, item.title, str(item.rss), item.description)})
            no += 1
        #print self.itemDataMap
        index = self.GetItemCount()
        for key, value in self.itemDataMap.items():
            dist = self.InsertStringItem(index, value[0])
            try:
                self.SetStringItem(dist, 1, value[1])
                self.SetStringItem(dist, 2, value[2])
                self.SetStringItem(dist, 3, value[3][0:50])
                self.SetItemData(index, key)
            except TypeError:
                self.DeleteItem(dist)
            index += 1
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(3, 500)

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
""" """
class MainWin(wx.Frame):
    def __init__(self, libraryfilepath, libraryfilename, *args, **kwargs):
        if os.path.exists('window.nco'):
            ff = open('window.nco')
            try:  data = pickle.load(ff)
            except:  data={'size':(800,600), 'pos':(0,0)}
            finally:  ff.close()
        else:  data={'size':(800,600), 'pos':(0,0)}

        wx.Frame.__init__(self, size=data['size'], pos=data['pos'], *args, **kwargs)
        self.CreateStatusBar()
        self.menuBar = wx.MenuBar()
        self.log = LogWin(self)
        self.note = MovieListCtrl(libraryfilepath, libraryfilename, parent=self)
        self.btn = wx.Button(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.btn, 0, wx.EXPAND)
        sizer.Add(self.note, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer)
        
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnButton(self, evt):
        print self.note.listctrl.FindItem(-1, 'sm10393864')
        
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
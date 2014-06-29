
#coding: utf-8
'''
Created on 2012/05/14

@author: Dev
'''
import modules.formats as Formats
import os
import sys
import underpanel
import wx

class Watchelper(wx.Panel):
    def __init__(self, path, name, log, *args, **kw):
        wx.Panel.__init__(self, *args, **kw)
        self.WF = Formats.WatcherFormats(path, name)
        self.WF.load()

        # Wigets
        self.ptop = wx.Panel(self)
        self.punder = underpanel.UnderPanel(parent=self)
        self.cfile = self.punder.filectrl
        self.cfolder = self.punder.folderctrl
        self.bappendfile = self.punder.folderbtn
        self.bplay = wx.Button(self.ptop, label=u'Play')
        self.bplayformer = wx.Button(self.ptop, label=u'Play former')
        self.bplaylatter = wx.Button(self.ptop, label=u'Play Latter')
        # Sizer
        sizer0 = wx.BoxSizer(wx.VERTICAL)
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.bplaylatter, 1, wx.EXPAND)
        sizer1.Add(self.bplay, 1, wx.EXPAND|wx.SOUTH|wx.EAST, border=1)
        sizer1.Add(self.bplayformer, 1, wx.EXPAND)
        self.ptop.SetSizer(sizer1)
        sizer0.Add(self.ptop, 0, wx.EXPAND)
        sizer0.Add(self.punder, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer0)
        # Bind
        self.Bind(wx.EVT_BUTTON, self.OnPlayButton, self.bplay)
        self.Bind(wx.EVT_BUTTON, self.OnPlayFormerButton, self.bplayformer)
        self.Bind(wx.EVT_BUTTON, self.OnPlayLatterButton, self.bplaylatter)
        self.Bind(wx.EVT_BUTTON, self.OnAppendFileButton, self.bappendfile)
        #self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnFileSelected, self.cfile)
        #self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnFolderSelected, self.cfolder)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnFolderItemActivated, self.cfolder)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDclick)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.OnSize(None)

        # data
        print self.WF

    def appendFolder(self, evt):
        dlg = wx.DirDialog(self, message=u'Choose a Folder!', style=wx.DD_DEFAULT_STYLE|wx.DD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if not(type(path) == unicode):  path = path.decode(sys.getfilesystemencoding())
        dlg.Destroy()
        #-- ライブラリに登録
        format =  self.filelist_update(path)
        #-- リストにフォルダを追加
        self.punder.ListCtrlAppendFolder(format)

    def play(self, index=None):
        """
        If index is None/bool, play currently checked.
        """
        if (index == None) or (type(index) == bool):
            if not self.cfile.getCheckedItemIndex():
                print('non checked')
                return False
            # Play currently
            print('Play Current')
            index = self.cfile.getCheckedItemIndex()
        else:
            # Play index
            print('Play index')
        self.cfile.setCheck(index)
        filedata = self.cfile.getCheckedItemData()
        #--- Play File ------

    def playFormer(self):
        print('Play former')
        index = self.cfile.getCheckedItemIndex()
        if (index == 0) or (not index):
            print "Error! don't have play former"
        else:
            self.play(index-1)

    def playLatter(self):
        print('Play Latter')
        index = self.cfile.getCheckedItemIndex()
        if (index >= self.cfile.GetItemCount()) or (not index):
            print "Error! don't have latter"
        else:
            self.play(index+1)

    def OnFileSelected(self, evt):
        print 'File Selected'
    def OnFolderSelected(self, evt):
        print 'Folder Selected'
    def OnAppendFileButton(self, evt):
        self.appendFolder(evt)
        return True
    def OnPlayButton(self, evt):
        self.play()
    def OnPlayFormerButton(self, evt):
        self.playFormer()
    def OnPlayLatterButton(self, evt):
        self.playLatter()

    def OnFolderItemActivated(self, evt):
        """On Enter or Doubleclicked"""
        folder = self.cfolder.getSelectedItemData()
        if not folder:  return False
        self.cfile.DeleteAllItems()
        self.punder.CheckListCtrlAppendFile(folder)
        #print 'FolderItemActivated'

    def OnLeftDclick(self, evt):
        print 'Double Clicked'

    def filelist_update(self, folder):
        """Find the file saved to the DB on the folder"""
        files = []
        for dirpath, dirnames, filenames in os.walk(folder):
            del dirpath, dirnames
            for filename in filenames:
                if os.path.splitext(filename)[-1].split(u'.')[-1] in self.WF.Data.exts:
                    files.append(filename)
            break
        format = self.WF.make_filefolder(folder, files)
        self.WF.append_library2(format)
        return format

    def OnSize(self, evt):
        self.cfile.setColumnWidthMax()
        self.cfolder.setColumnWidthMax()
        if evt == None:  pass
        else:
            evt.Skip()
            
    def OnClose(self, evt):
        evt.Skip()

if __name__ == '__main__':
    class Win(wx.Frame):
        def __init__(self, path, name, *args, **kw):
            wx.Frame.__init__(self, *args, **kw)
            self.panel = Watchelper(parent=self, path=path, name=name, log=None)


    app = wx.App(False)
    #---  -------
    win = Win(path='c:\\Users\\Dev\\Desktop', name="libtest.txt", parent=None)
    pan = win.panel
    win.Show()
    app.MainLoop()

    """
    pan.filelist_update('c:\\Users\\Dev\\Desktop')#\\test1')
    pan.WF.save()
    print pan.WF.get_lib('c:\\Users\\Dev\\Desktop')#\\test1')
    """






        
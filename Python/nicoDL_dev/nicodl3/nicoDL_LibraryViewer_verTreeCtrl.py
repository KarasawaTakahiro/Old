# coding: utf-8

import modules.nicodl_various as Various
import wx


class MyTreeCtrl(wx.TreeCtrl):
    def __init__(self, parent):
        wx.TreeCtrl.__init__(self, parent, style=wx.TR_DEFAULT_STYLE)
        
    def OnCompareItems(self, item1, item2):
        t1 = self.GetItemText(item1)
        t2 = self.GetItemText(item2)
        print('compare: ' + t1 + ' <> ' + t2 + '\n')
        if t1 < t2: return -1
        if t1 == t2: return 0
        return 1
    
class LibraryViewer_Panel(wx.Panel):
    def __init__(self, parent, libfilepath):
        wx.Panel.__init__(self, parent=parent, style=wx.WANTS_CHARS)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
        various = Various.nicoDL_Various(libfilepath)

        """TreeCtrl"""
        self.tree = MyTreeCtrl(self)

        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
        fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))

        self.tree.SetImageList(il)
        self.il = il
        
        self.root = self.tree.AddRoot("Library")
        self.tree.SetPyData(self.root, None)
        self.tree.SetItemImage(self.root, fldridx, wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(self.root, fldropenidx, wx.TreeItemIcon_Expanded)

        
        for x in various.getmylistIDs():
            child = self.tree.AppendItem(self.root, various.pickup(mylist_id=x, choice='mylist_name'))
            self.tree.SetPyData(child, None)
            self.tree.SetItemImage(child, fldridx, wx.TreeItemIcon_Normal)
            self.tree.SetItemImage(child, fldropenidx, wx.TreeItemIcon_Expanded)

            for y in various.pickup(mylist_id=x, choice='downloaded'):
                last = self.tree.AppendItem(child, u'%s %s'%(y, various.pickup(movie_id=y,  choice='movie_name')))
                self.tree.SetPyData(last, None)
                self.tree.SetItemImage(last, fileidx, wx.TreeItemIcon_Normal)
                self.tree.SetItemImage(last, fileidx, wx.TreeItemIcon_Expanded)

        for x in various.getmovieIDs():
            child = self.tree.AppendItem(self.root,  u'%s %s'%(x, various.pickup(movie_id=x,  choice='movie_name')))
            self.tree.SetPyData(child, None)
            self.tree.SetItemImage(child, fileidx, wx.TreeItemIcon_Normal)
            self.tree.SetItemImage(child, fileidx, wx.TreeItemIcon_Expanded)

        self.tree.Expand(self.root)
        """
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed, self.tree)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)
        self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginEdit, self.tree)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndEdit, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate, self.tree)

        self.tree.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        self.tree.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.tree.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)"""

    def OnSize(self, event):
        w,h = self.GetClientSizeTuple()
        self.tree.SetDimensions(0, 0, w, h)
        
class LibraryViewer_Win(wx.Frame):
    def __init__(self, title, libfilepath):
        wx.Frame.__init__(self, None, title=title)
        self.panel = LibraryViewer_Panel(parent=self, libfilepath=libfilepath)
        self.Show()
        
if __name__ == '__main__':
    import os
    libfilepath = os.path.join(os.getcwd(), ur'data')
    try:
        app = wx.App()
        win = LibraryViewer_Win(title='nicoDL Library Viewer', libfilepath=libfilepath)
    except BaseException, mess:  print mess
    app.MainLoop()
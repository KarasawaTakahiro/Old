# coding: utf-8


import os
import sys
import wx
import wx.gizmos as gizmos

import modules.nicodl_various as Various
import modules.nicovideoAPI as API 


class MainPanel(wx.Panel):
    def __init__(self, parent, liblocate):
        wx.Panel.__init__(self, parent)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.tree = gizmos.TreeListCtrl(self, id=-1, style=wx.TR_DEFAULT_STYLE|wx.TR_FULL_ROW_HIGHLIGHT)

        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        self.fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        self.fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
        self.fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))

        self.tree.SetImageList(il)
        self.il = il

        self.tree.AddColumn(u'名前')
        self.tree.AddColumn(u'状態')
        self.tree.AddColumn(u'ID')
        self.tree.AddColumn(u'form')
        self.tree.SetMainColumn(0)
        self.tree.SetColumnWidth(0, 170)
        """ライブラリデータセット"""
        # 既存のライブラリ
        #data = Various.nicoDL_Various(liblocate, 'Library.ndl')
        #data = data.libopen()
        # ビュワー用
        #self.various = Various.nicoDL_Various(liblocate, '_Library.ndl')
        #self.various.libopen()
        #self.various.save(data)
        """"""
        ###########
        self.various = Various.nicoDL_Various(liblocate, 'Library.ndl')
        self.mylists = self.various.getmylistIDs()
        self.movies = self.various.getmovieIDs()
        # root
        self.root = self.tree.AddRoot('LibraryFile')
        self.tree.SetItemText(self.root, '',  1)
        self.tree.SetItemText(self.root, '',  2)
        self.tree.SetItemText(self.root, '',  3)
        self.tree.SetItemImage(self.root, self.fldridx, which = wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(self.root, self.fldropenidx, which = wx.TreeItemIcon_Expanded)
        # MOVIE
        self.child_movie = self.tree.AppendItem(self.root, u'動画')
        self.tree.SetItemText(self.child_movie, '', 1)
        self.tree.SetItemText(self.child_movie, '', 2)
        self.tree.SetItemText(self.child_movie, '', 3)
        self.tree.SetItemImage(self.child_movie, self.fldridx, which = wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(self.child_movie, self.fldropenidx, which = wx.TreeItemIcon_Expanded)
        for item in self.various.getmovieIDs():
            try:
                last = self.tree.AppendItem(self.child_movie, str(self.various.pickup(movie_id=item, choice='movie_name')))
                self.tree.SetItemText(last, str(self.various.pickup(movie_id=item, choice='state')), 1)
                self.tree.SetItemText(last, self.various.pickup(movie_id=item, choice='movie_id'), 2)
                self.tree.SetItemText(last, self.various.pickup(movie_id=item, choice='form'), 3)
                self.tree.SetItemImage(last, self.fileidx, which = wx.TreeItemIcon_Normal)
                self.tree.SetItemImage(last, self.fileidx, which = wx.TreeItemIcon_Expanded)
            except ValueError, mess:  print mess
        # MYLIST
        self.child_mylist = self.tree.AppendItem(self.root, u'マイリスト')
        self.tree.SetItemText(self.child_mylist, '', 1)
        self.tree.SetItemText(self.child_mylist, '', 2)
        self.tree.SetItemText(self.child_mylist, '', 3)
        self.tree.SetItemImage(self.child_mylist, self.fldridx, which = wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(self.child_mylist, self.fldropenidx, which = wx.TreeItemIcon_Expanded)
        for item in self.various.getmylistIDs():
            if not self.various.pickup(mylist_id=item, choice='mylist_name'):
                mylistname = u'不明'
            else: mylistname = self.various.pickup(mylist_id=item, choice='mylist_name')
            last = self.tree.AppendItem(self.child_mylist, mylistname)
            self.tree.SetItemText(last, str(self.various.pickup(mylist_id=item, choice='rss')), 1)
            self.tree.SetItemText(last, self.various.pickup(mylist_id=item, choice='mylist_id'), 2)
            self.tree.SetItemText(last, self.various.pickup(mylist_id=item, choice='form'), 3)
            self.tree.SetItemImage(last, self.fldridx, which = wx.TreeItemIcon_Normal)
            self.tree.SetItemImage(last, self.fldropenidx, which = wx.TreeItemIcon_Expanded)
            for i in self.various.pickup(mylist_id=item, choice='downloaded'):
                child = self.tree.AppendItem(last, str(self.various.pickup(movie_id=i, choice='movie_name')))
                self.tree.SetItemText(child, str(self.various.pickup(movie_id=i, choice='state')), 1)
                self.tree.SetItemText(child, self.various.pickup(movie_id=i, choice='movie_id'), 2)
                self.tree.SetItemText(child, self.various.pickup(movie_id=i, choice='form'), 3)
                self.tree.SetItemImage(child, self.fileidx, which = wx.TreeItemIcon_Normal)
                self.tree.SetItemImage(child, self.fileidx, which = wx.TreeItemIcon_Expanded)

        self.tree.Expand(self.root)
        
        self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        #self.tree.GetMainWindow().Bind(wx.EVT_LIST_BEGIN_DRAG, self.OnColDrag)

    def dataset(self):
        # root
        self.root = self.tree.AddRoot('LibraryFile')
        self.tree.SetItemText(self.root, '',  1)
        self.tree.SetItemText(self.root, '',  2)
        self.tree.SetItemText(self.root, '',  3)
        self.tree.SetItemImage(self.root, self.fldridx, which = wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(self.root, self.fldropenidx, which = wx.TreeItemIcon_Expanded)
        # MOVIE
        self.child_movie = self.tree.AppendItem(self.root, u'動画')
        self.tree.SetItemText(self.child_movie, '', 1)
        self.tree.SetItemText(self.child_movie, '', 2)
        self.tree.SetItemText(self.child_movie, '', 3)
        self.tree.SetItemImage(self.child_movie, self.fldridx, which = wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(self.child_movie, self.fldropenidx, which = wx.TreeItemIcon_Expanded)
        for item in self.various.getmovieIDs():
            try:
                last = self.tree.AppendItem(self.child_movie, str(self.various.pickup(movie_id=item, choice='movie_name')).decode('utf-8'))
                self.tree.SetItemText(last, str(self.various.pickup(movie_id=item, choice='state')), 1)
                self.tree.SetItemText(last, self.various.pickup(movie_id=item, choice='movie_id'), 2)
                self.tree.SetItemText(last, self.various.pickup(movie_id=item, choice='form'), 3)
                self.tree.SetItemImage(last, self.fileidx, which = wx.TreeItemIcon_Normal)
                self.tree.SetItemImage(last, self.fileidx, which = wx.TreeItemIcon_Expanded)
            except ValueError, mess:  print mess
        # MYLIST
        self.child_mylist = self.tree.AppendItem(self.root, u'マイリスト')
        self.tree.SetItemText(self.child_mylist, '', 1)
        self.tree.SetItemText(self.child_mylist, '', 2)
        self.tree.SetItemText(self.child_mylist, '', 3)
        self.tree.SetItemImage(self.child_mylist, self.fldridx, which = wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(self.child_mylist, self.fldropenidx, which = wx.TreeItemIcon_Expanded)
        for item in self.various.getmylistIDs():
            if not self.various.pickup(mylist_id=item, choice='mylist_name'):
                mylistname = u'不明'
            else: mylistname = self.various.pickup(mylist_id=item, choice='mylist_name').decode('utf-8')
            last = self.tree.AppendItem(self.child_mylist, mylistname)
            self.tree.SetItemText(last, str(self.various.pickup(mylist_id=item, choice='rss')), 1)
            self.tree.SetItemText(last, self.various.pickup(mylist_id=item, choice='mylist_id'), 2)
            self.tree.SetItemText(last, self.various.pickup(mylist_id=item, choice='form'), 3)
            self.tree.SetItemImage(last, self.fldridx, which = wx.TreeItemIcon_Normal)
            self.tree.SetItemImage(last, self.fldropenidx, which = wx.TreeItemIcon_Expanded)
            for i in self.various.pickup(mylist_id=item, choice='downloaded'):
                child = self.tree.AppendItem(last, str(self.various.pickup(movie_id=i, choice='movie_name').decode('utf-8')))
                self.tree.SetItemText(child, str(self.various.pickup(movie_id=i, choice='state')), 1)
                self.tree.SetItemText(child, self.various.pickup(movie_id=i, choice='movie_id'), 2)
                self.tree.SetItemText(child, self.various.pickup(movie_id=i, choice='form'), 3)
                self.tree.SetItemImage(child, self.fileidx, which = wx.TreeItemIcon_Normal)
                self.tree.SetItemImage(child, self.fileidx, which = wx.TreeItemIcon_Expanded)
    
        self.tree.Expand(self.root)

    def datareset(self):
        self.tree.DeleteAllItems()
        self.dataset()

    def OnColDrag(self, evt):
        print 
        print dir(evt)
        print 

    def OnSize(self, evt):
        if hasattr(self, 'tree'):
            self.tree.SetSize(self.GetSize())

    def OnRightUp(self, evt):
        """
        OnRightUpの時点でself.myformIDに値を入れ、それを利用してupdate()する
        """
        self.myformID = None
        self.selectedcolpos = self.tree.HitTest(evt.GetPosition())[2]
        self.selecteditem = self.tree.HitTest(evt.GetPosition())[0]
        #print 'selecteditem:', self.selecteditem
        #print 'HitTest:', self.tree.HitTest(evt.GetPosition())
        #print 'getpos:', evt.GetPosition()
        if self.selecteditem:
            self.myformID = self.tree.GetItemText(self.selecteditem, 2)
            #print 'myformID:', self.myformID

        if not hasattr(self, 'popup1ID'):
            self.popup1ID = wx.NewId()
            self.popup2ID = wx.NewId()

            self.Bind(wx.EVT_MENU, self.OnPopup1, id=self.popup1ID)
            self.Bind(wx.EVT_MENU, self.OnPopup2, id=self.popup2ID)

        menu = wx.Menu()
        
        menu.Append(self.popup1ID, u'Data Update')
        menu.Append(self.popup2ID, u'Delete')
        
        self.PopupMenu(menu)
        menu.Destroy()

    def OnPopup1(self, evt):
        """情報のアップデートの関数"""
        print int(self.selectedcolpos)
        if int(self.selectedcolpos) == 0:
        # 名前を選択したとき
            if self.myformID.find('sm') > -1:
                movie_id = self.myformID
                api = API.Nicovideo(movie_id=self.myformID)
                self.various.rewrite_library(factor='movie_name', value=api.get_movie_title(), movie_id=movie_id)
            elif (self.myformID.find('sm') == -1) and (not self.myformID == ''):
                # (not self.myformID == '')は動画やマイリストの部分を選択した場合
                mylist_id = self.myformID
                api = API.Nicovideo(mylist_id=self.myformID)
                self.various.rewrite_library(factor='mylist_name', value=api.get_mylist_name(), mylist_id=mylist_id)
        elif int(self.selectedcolpos) == 1:
        # 状態を選択したとき
            state = self.tree.GetItemText(self.selecteditem, 1)
            print state
            if state == 'False':  state = True
            else:  state = False
            if self.myformID.find('sm') > -1:
                movie_id = self.myformID
                self.various.rewrite_library(factor='state', value=state, movie_id=movie_id)
            elif (self.myformID.find('sm') == -1) and (not self.myformID == ''):
                # (not self.myformID == '')は動画やマイリストの部分を選択した場合
                mylist_id = self.myformID
                self.various.rewrite_library(factor='rss', value=state, mylist_id=mylist_id)
                
        self.datareset()
        
    def OnPopup2(self, evt):
        """
        *アイテム削除関数
        self.selecteditem, self.myformIDはself.OnRightUpで定義される
        """
        #print 'OnPopup2'
        movie_id_list = []
        mylist_id_list = []
        if self.myformID.find('sm') > -1:
            movie_id_list.append(self.myformID)
        elif (self.myformID.find('sm') == -1) and (not self.myformID == ''):
            # (not self.myformID == '')は動画やマイリストの部分を選択した場合
            mylist_id_list.append(self.myformID)
        # 動画を削除した時にマイリスから来ていればそのマイリスのDL済みから動画ID削除
        for item in movie_id_list:
            if self.various.pickup(movie_id=item, choice='mylist_id'):
                myid = self.various.pickup(movie_id=item, choice='mylist_id')
                self.various.rewrite_library(factor='downloaded', value=item, mylist_id=myid, chengedownloaded=-1)
        # マイリスを削除した時に含まれる動画情報を削除に追加
        for item in mylist_id_list:
            movie_id_list.extend(self.various.pickup(mylist_id=item, choice='downloaded'))
        # libファイルから削除
        errors = self.various.deldata(movie_id_list=movie_id_list, mylist_id_list=mylist_id_list)
        if errors:
            # 削除できないものがあった時
            errors.insert(0, u'削除できませんでした')  # メッセージ追加
            dlg = wx.MessageDialog(self, '\n'.join(errors), 'Message', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        # リストから削除
        self.tree.Delete(self.selecteditem)


class MainFrame(wx.Frame):
    def __init__(self, libfile):
        wx.Frame.__init__(self, None, -1, title='LibraryViewer', size=(800, 320))
        try: 
            self.panel = MainPanel(self, liblocate=libfile)
        except BaseException, mess:
            print mess
            print sys.stderr

        self.Show()

if __name__ == '__main__':
    print os.getcwd()
    path = 'data'
    app = wx.App()
    win = MainFrame(path)
    win.Show()
    app.MainLoop()
    
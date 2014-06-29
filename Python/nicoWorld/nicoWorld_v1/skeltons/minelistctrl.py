
# coding: utf-8
"""
created on 2012/04/18
created by KarasawaTakahiro
"""

import wx

if __name__ == '__main__':
    from modules import formats
    FORMATS = formats.LibraryFormat('.\\..\\data', 'Library.nco')
    FORMATS.load()
    
    data = {}
    c = 0
    for item in FORMATS.getAllMovieMyformat():
        data.update({c:[item.ID, item.title, item.state, item.description, item.mylist_id]})
        c += 1
    print data

class MySortListCtrl(wx.ListCtrl):
    def __init__(self, *args, **kwargs):
        """styleは指定してはいけない"""
        wx.ListCtrl.__init__(self, style=wx.LC_REPORT
                                             | wx.BORDER_NONE
                                             | wx.LC_EDIT_LABELS
                                             | wx.WANTS_CHARS,
                                    *args, **kwargs)

        self._sortOrder = None
        self._prvCol = None
        self._SelectedCol = None
        
        self.Bind(wx.EVT_LIST_COL_CLICK, self.Sort)
        
    def Sort(self, evt):
        """ソートする"""
        self._SelectedCol = evt.GetColumn()
        if self._prvCol == self._SelectedCol:
            self._sortOrder = not self._sortOrder
        else:
            self._sortOrder = True
        if self._sortOrder:
            self.AscendingCmp(self._SelectedCol)
        else:
            self.DescendingCmp(self._SelectedCol)
        self.DeleteAllItems()
        self.Load()
        self._prvCol =  self._SelectedCol

    """以下の関数をオーバーライドして使う"""
    def AscendingCmp(self, col):
        """データを昇順に並び替える関数
        col: 選択された列"""
        raise ValueError, u'関数を定義してください'
    def DescendingCmp(self, col):
        """データを降順に並び替える関数
        col: 選択された列"""
        raise ValueError, u'関数を定義してください'
    def Load(self):
        """データをリストに並べる関数（元のItemsを削除する必要はない）"""
        raise ValueError, u'関数を定義してください'

class MovieListCtrl(MySortListCtrl):
    def __init__(self, *args, **kwargs):
        MySortListCtrl.__init__(self, *args, **kwargs)
        
        self.data = data
        self.InsertColumn(0,u'動画ID')
        self.InsertColumn(1, u'タイトル')
        self.InsertColumn(2, u'DL')
        self.InsertColumn(3, u'説明')
        self.InsertColumn(3, u'マイリス')
        self.Load()
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(3, 500)
        self.SetColumnWidth(4, wx.LIST_AUTOSIZE)

    def Load(self):
        index = self.GetItemCount()
        for key, value in self.data.items():
            print index, value
            dist = self.InsertStringItem(index, value[0])
            self.SetStringItem(dist, 1, value[1])
            self.SetStringItem(dist, 2, str(value[2]))
            self.SetStringItem(dist, 3, value[3][:50])
            self.SetStringItem(dist, 4, str(value[4]))
            self.SetItemData(index, key)
            index += 1

    def AscendingCmp(self, col):
        print u'昇順'
        li = []
        for value in self.data.itervalues():
            li.append(value)
        if col == 0:
            li.sort(cmp=self.movieIDcmp)
        elif col == 4:
            li.sort(cmp=self.mylistIDcmp)
        elif col == 2:
            li.sort(cmp=self.Boolcmp)
        else:
            li.sort()
        index = 0
        itemMap = {}
        for item in li:
            itemMap.update({index:item})
            index += 1
        self.data =  itemMap
        
    def DescendingCmp(self, col):
        print u'降順'
        li = []
        for value in self.data.itervalues():
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
        self.data =  itemMap
    
    def movieIDcmp(self, item1, item2):
        return cmp(int(item1[0][2:]), int(item2[0][2:]))
    def mylistIDcmp(self, item1, item2):
        print 'item1:', item1[4]
        print 'item2:', item2[4]
        """itemはintかFalse"""
        if not item1[4]:
            # item1[4] == False
            return 1
        elif not item2[4]:
            # item2[4] == False
            return -1
        elif (not item1[4]) and (not item2[4]):
            # item1[4] == item2[4] == False
            return 0
        elif (type(item1[4]) == bool or type(item2[4]) == int): 
            # bool and int
            return -1
        elif (type(item2[4]) == int)  or (type(item2[4]) == bool):
            # int and bool
            return 1
        else:
            # item1[4] == item2[4] == int
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

class MainWin(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        listctrl = MovieListCtrl(self,)

if __name__ == '__main__':
    app = wx.App(redirect=False)
    win = MainWin(parent=None)
    win.Show()
    app.MainLoop()
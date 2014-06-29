
# coding: utf-8
"""
created on 2012/04/18
created by KarasawaTakahiro
"""

import wx

data = {0:['sm54', 'titlef', True, False],
        1:['sm1', 'title2', True, '49'],
        2:['sm4', 'title22', True, '4'],
        3:['sm6', 'title23', False, '44'],
        4:['sm34', 'title21', True, '444'],
        5:['sm14', 'title27', False, '46'],
        6:['sm11', 'title232', False, '41'],
        }

class MySortListCtrl(wx.ListCtrl):
    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, style=wx.LC_REPORT
                                             | wx.BORDER_NONE
                                             | wx.LC_EDIT_LABELS
                                             | wx.WANTS_CHARS,
                                    *args, **kwargs)
        
        self.sortOrder = None
        self.prvCol = None
        self.SelectedCol = 0
        
        self.Bind(wx.EVT_LIST_COL_CLICK, self.Sort)
        
    def Sort(self, evt):
        self.SelectedCol = evt.GetColumn()
        if self.prvCol == self.SelectedCol:
            self.sortOrder = not self.sortOrder
        else:
            self.sortOrder = True
        if self.sortOrder:
            self.AscendingCmp(self.SelectedCol)
        else:
            self.DescendingCmp(self.SelectedCol)
        self.DeleteAllItems()
        self.Load()
        self.prvCol =  self.SelectedCol

    """以下の関数をオーバーライドして使う"""
    def AscendingCmp(self, col):
        """昇順に並び替える関数"""
        raise ValueError, u'関数を定義してください'
    def DescendingCmp(self, col):
        """降順に並び替える関数"""
        raise ValueError, u'関数を定義してください'
    def Load(self):
        """リストに並べる関数（元のItemsを削除する必要はない）"""
        raise ValueError, u'関数を定義してください'


class MovieListCtrl(MySortListCtrl):
    def __init__(self, *args, **kwargs):
        MySortListCtrl.__init__(self, *args, **kwargs)
        
        self.data = data
        self.InsertColumn(0,u'ID')
        self.InsertColumn(1, u'title')
        self.InsertColumn(2, u'state')
        self.InsertColumn(3, u'mylist')
        self.Load()
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(3, 500)

    def Load(self):
        index = self.GetItemCount()
        for key, value in self.data.items():
            print index, value
            dist = self.InsertStringItem(index, value[0])
            self.SetStringItem(dist, 1, value[1])
            self.SetStringItem(dist, 2, str(value[2]))
            self.SetStringItem(dist, 3, str(value[3]))
            self.SetItemData(index, key)
            index += 1

    def AscendingCmp(self, col):
        print u'昇順'
        li = []
        for value in self.data.itervalues():
            li.append(value)
        if col == 0:
            li.sort(cmp=self.movieIDcmp)
        elif col == 3:
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
        elif col == 3:
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
        print 'item1:', item1
        print 'item2:', item2
        """itemはintかFalse"""
        if not item1[3]:
            # item1[3] == False
            return 1
        elif not item2[3]:
            # item2[3] == False
            return -1
        elif (not item1[3]) and (not item2[3]):
            # item1[3] == item2[3] == False
            return 0
        else:
            # item1[3] == item2[3] == int
            return cmp(int(item1[3]), int(item2[3]))
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
        
        
class MainWin(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        listctrl = MovieListCtrl(self,)
        
if __name__ == '__main__':
    app = wx.App(redirect=False)
    win = MainWin(parent=None)
    win.Show()
    app.MainLoop()
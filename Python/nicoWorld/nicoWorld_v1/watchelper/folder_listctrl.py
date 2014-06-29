#coding: utf-8
'''
Created on 2012/05/13

@author: Dev
'''
import skeltons.minelistctrl as minelc
import wx

class FolderListCtrl(minelc.MySortListCtrl):
    def __init__(self, data=None, *args, **kw):
        """
        data: [[col0...], []]
        """
        minelc.MySortListCtrl.__init__(self, *args, **kw)

        self.selected = None
        self.Data = {}
        if self.Data:
            index = 0
            for item in self.Data:
                self.Data.update({index:item})
                index += 1
                
        #
        self.InsertColumn(0, u'')
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._OnListItemSelected)
    def appendData(self, data):
        index = self.GetItemCount()
        self.Data.update({index:data})
        return index
    def getListItemSelected(self):
        return self.selected
    def getSelectedItemData(self):
        if self.selected:
            return self.Data[self.selected]
        else:
            return False
    def setColumnWidthMax(self):
        self.SetColumnWidth(0, self.GetSizeTuple()[0])
        
    def OnDoubleClick(self, evt):
        print 'OnDoubleClicked'
        evt.Skip()


    def _OnListItemSelected(self, evt):
        self.selected = evt.GetIndex()
        evt.Skip()
        
    def AscendingCmp(self, col):
        raise ValueError, 'not setting'
    def DescendingCmp(self, col):
        raise ValueError, 'not setting'
    def Load(self):
        for index, value in self.Data.items():
            self.InsertStringItem(index, value)


if __name__ == '__main__':
    class MainWin(wx.Frame):
        def __init__(self, *args, **kw):
            wx.Frame.__init__(self, *args, **kw)
            self.lc = FolderListCtrl(parent=self)
            count = 0
            for item in u'fgagteashbrga':
                self.lc.Data.update({count:item})
                count += 1
            self.lc.Load()
    
    app = wx.App(redirect=False)
    win = MainWin(parent=None)
    win.Show()
    app.MainLoop()
        
        
        
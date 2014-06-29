
# coding: utf-8
"""
created on 2012/05/09
created by KarasawaTakahiro
"""
import skeltons.minelistctrl as minelc
import wx
from wx.lib.mixins.listctrl import CheckListCtrlMixin

class FileCheckListCtrl(minelc.MySortListCtrl, CheckListCtrlMixin):
    def __init__(self, data=None, *args, **kw):
        """
        data: [value, value, value,]
              -data is list of value
              -if direct, format of self.Data is self.Data={index:value, index:value, index:value, }
        """
        minelc.MySortListCtrl.__init__(self, *args, **kw)
        CheckListCtrlMixin.__init__(self)

        self._checked_former = None
        self._checked_latter = None
        self.selected = None
        self.checked = None

        # Data = {index:value, index:value, index:value, }
        self.Data = {}
        if not(data==None):
            index = 0
            for item in data:
                self.Data.update({index:item})
                index += 1
        else:
            self.Data = {}
        # 
        self.InsertColumn(0, u'')
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._OnListItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)  # CheckListCtrlMixin

    def appendData(self, data):
        index = self.GetItemCount()
        self.Data.update({index:data})
        return index
    def getCheckedItemIndex(self):
        return self._checked_former
    def getSelectedItemIndex(self):
        return self.selected
    def getCheckedItemData(self):
        if not(self._checked_former == None):
            return self.Data[self._checked_former]
        else:
            return False
    def getSelectedItemData(self):
        if not(self.selected == None):
            return self.Data[self.selected]
        else:
            return False
    def getIndexData(self, index):
        if index > len(self.Data):
            raise IndexError
        else:
            return self.Data[index]
    def setColumnWidthMax(self):
        self.SetColumnWidth(0, self.GetSizeTuple()[0])
    def setCheck(self, index):
        if index > len(self.Data):
            raise IndexError, 'index over'
        else:
            self.CheckItem(index, True)

    def OnCheckItem(self, index, flag):
        """
        we can select one of elements.
        """
        if flag:
            self._checked_latter = self._checked_former
            self._checked_former = index
            if not(self._checked_latter == None):
                self.CheckItem(self._checked_latter, False)
            self.checked = self._checked_former

    def _OnListItemSelected(self, evt):
        self.selected = evt.GetIndex()
        evt.Skip()

    def AscendingCmp(self, col):
        raise ValueError, 'no setting'
    def DescendingCmp(self, col):
        raise ValueError, 'no setting'
    def Load(self):
        for key, value in self.Data.items():
            self.InsertStringItem(key, value)

    def OnItemActivated(self, evt):
        """CheckListCtrlMixin"""
        self.ToggleItem(evt.m_itemIndex)

if __name__ == '__main__':
    class MainWin(wx.Frame):
        def __init__(self, *args, **kwargs):
            wx.Frame.__init__(self, *args, **kwargs)
            self.lc = FileCheckListCtrl(self)
            count = 0
            for item in u'abcdefghijklmnopqrstuvwxyz':
                self.lc.Data.update({count:item})
                count += 1
            self.lc.Load()
            self.btn = wx.Button(self)
            self.Bind(wx.EVT_BUTTON, self.OnButton)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.btn, 0, wx.EXPAND)
            sizer.Add(self.lc, 1, wx.EXPAND)
            self.SetSizerAndFit(sizer)
        def OnButton(self, evt):
            self.lc.OnButton(evt)

    app = wx.App(redirect=False)
    win = MainWin(parent=None)
    win.Show()
    app.MainLoop()
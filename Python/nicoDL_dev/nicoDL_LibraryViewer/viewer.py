#coding: utf-8
u"""
wxpython demo ListCtrl 参照
"""

import wx
import wx.lib.mixins.listctrl as listmix

class TestList(wx.ListCtrl, listmix.TextEditMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

        listmix.TextEditMixin.__init__(self)

        self.InsertColumn(0, "ID")
        self.InsertColumn(1, "Name")
        self.InsertColumn(2, "Path")

        self.SetColumnWidth(0, 100)
        self.SetColumnWidth(1, 100)
        self.SetColumnWidth(2, 100)
        self.InsertStringItem(0, '1')
        self.InsertStringItem(1, '2')
        self.InsertStringItem(2, '3')

        self.SetStringItem(0, 1, "0")
        self.SetStringItem(0, 2, "0.777")
        self.SetStringItem(1, 1, "0.1")
        self.SetStringItem(1, 2, "1.222")
        self.SetStringItem(2, 1, "0.2")
        self.SetStringItem(2, 2, "5.333")

        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)

    def OnColClick(self, evt):
        col = evt.GetColumn()
        print self.GetItem(0, col).GetText()
        print self.GetItem(1, col).GetText()
        print self.GetItem(2, col).GetText()

class MyApp(wx.PySimpleApp):
    def OnInit(self):
        Frm = wx.Frame(None, -1, 'Title', size=(300, 250))
        self.p = wx.Panel(Frm, -1)

        jl = TestList(self.p, 0, size=(300, 100),
                      style=wx.LC_REPORT|wx.LC_HRULES)

        Frm.Show()
        return True

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
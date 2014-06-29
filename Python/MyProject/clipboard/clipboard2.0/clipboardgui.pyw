# -*- coding: utf-8 -*-

import wx
import win32clipboard as cb

class clipboard(wx.Frame):

    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, title=u'クリップボードビュー', size=(500,400))
        self.panel = wx.Panel(self)

        wx.Button(self.panel, -1, u'更新', (230,290))

        self.Bind(wx.EVT_BUTTON, self.OnView, id=-1)


    def OnView(self, event):
        cb.OpenClipboard()
        text = cb.GetClipboardData(1)
        cb.CloseClipboard()

        wx.StaticText(self.panel, -1, text, (10,10))

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = clipboard(None, -1)
    frame.Show()
    app.MainLoop()

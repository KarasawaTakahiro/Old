#-*- coding: utf-8 -*-

import wx

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(400,400))
        #子サイザーを用意する(水平方向に整形)
        self.childSizer = wx.BoxSizer(wx.HORIZONTAL)
        #ボタンを作成する
        self.startButton =wx.Button(self, -1, "Start")
        self.stopButton =wx.Button(self, -1, "Stop")
        #子サイザーにボタンを追加する
        self.childSizer.Add(self.startButton, 0, wx.EXPAND)
        self.childSizer.Add(self.stopButton, 0, wx.EXPAND)
        #メインサイザーを用意する(垂直方向に整形)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        #テキストボックスとラベルを作成する
        self.textControl = wx.TextCtrl(self, size=(300,100), style=wx.TE_MULTILINE)
        self.label = wx.StaticText(self, label="Label :")
        #サイザーに追加する
        self.sizer.Add(self.textControl, 0, wx.EXPAND)
        self.sizer.Add(self.childSizer, 0, wx.ALIGN_CENTER)
        self.sizer.Add(self.label, 0, wx.EXPAND)
        #Frameにサイザーを追加する
        self.SetSizer(self.sizer)
        #サイザーのレイアウトを行う
        self.SetAutoLayout(1)
        self.sizer.Fit(self)

        self.Show()

app = wx.App(False)
frame = MainWindow(None, "sample")
app.MainLoop()
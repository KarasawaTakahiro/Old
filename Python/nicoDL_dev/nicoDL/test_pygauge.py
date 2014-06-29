# coding: utf-8

import time
import wx
import random

try:
    from agw import pygauge as PG
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.pygauge as PG

class MainWin(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="nicoDL",)
        self.panel = wx.Panel(self)
        self.gg = PG.PyGauge(self.panel, pos=(10,10), size=(100,10))
        self.btn = wx.Button(self.panel, pos=(10,30), label='push')
        print self.gg.GetRange()

        self.gg.SetBackgroundColour(wx.WHITE)  # 背景色
        self.btn.Bind(wx.EVT_BUTTON, self.OnButton3)

    def OnButton3(self, evt):
        value = random.randint(0,100)
        self.OnButton(value)

    def OnButton(self, value):
        u"""
        SetValue(塗りつぶす範囲)
        Refresh() 塗りつぶす
        """
        self.gg.SetValue(value)
        self.gg.Refresh()
        print self.gg.GetMaxClientSize()

    def OnButton2(self, evt):
        u"""
        Update(塗りつぶす範囲,
               塗りつぶしにかける時間（50ミリ秒の倍数）)
        """
        self.gg.Update(50, 2000)

if __name__ == '__main__':
    app = wx.App()
    win = MainWin()
    win.Show()
    app.MainLoop()

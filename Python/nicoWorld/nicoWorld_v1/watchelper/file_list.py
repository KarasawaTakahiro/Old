
# coding: utf-8
"""
created on 2012/05/09
created by KarasawaTakahiro
"""

import wx

class MainWin(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        
        
if __name__ == '__main__':
    app = wx.App(redirect=False)
    win = MainWin(parent=None)
    win.Show()
    app.MainLoop()
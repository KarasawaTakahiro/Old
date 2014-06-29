#coding: utf-8

import wx
import nicodl_various_beta as Various


class MainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent,)
        various = Various.nicoDL_Various(libraryfilepath=False)


class MainFrame(wx.Frame):
    def __init__(self,):
        wx.Frame.__init__(self, None, title=u'ライブラリビュワー')



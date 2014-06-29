#-*- coding: utf-8 -*-
import os, sys
import wx

class MainFrame(wx.Frame):
  def __init__(self):
    super(type(self), self).__init__(None) # 基底クラスのコンストラクタ呼び出し
    self._icon = wx.ArtProvider.GetIcon(wx.ART_QUESTION, wx.ART_OTHER, (16, 16)) # システムからアイコン取得
    self._tbi = wx.TaskBarIcon()
    self._tbi.SetIcon(self._icon, u'tips')
    self._tbi.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.onLDown)
    self.Bind(wx.EVT_ICONIZE, self.onIconized)
    self.Show()

  def onIconized(self, event):
    print 'Iconized!!'
    self.Hide()         # ウィンドウ非表示

  def onLDown(self, event):
    print 'LDown!!'
    self.Iconize(False) # 最小化解除
    self.Show(True)     # ウィンドウ表示
    self.Raise()        # ウィンドウをフォーカス

# main
app = wx.PySimpleApp()
app.SetTopWindow(MainFrame())
app.MainLoop()
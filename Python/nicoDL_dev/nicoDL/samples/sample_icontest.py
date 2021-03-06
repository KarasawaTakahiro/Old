#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import wx

def OnTaskBarRight(event):
             app.ExitMainLoop()

#setup app
app= wx.PySimpleApp()

#setup icon object
icon = wx.Icon("test.ico", wx.BITMAP_TYPE_ICO)

#setup taskbar icon
tbicon = wx.TaskBarIcon()
tbicon.SetIcon(icon, "I am an Icon")

#add taskbar icon event
wx.EVT_TASKBAR_RIGHT_UP(tbicon, OnTaskBarRight)

app.MainLoop()
#!/usr/bin/env python
# coding: utf-8


import wx
class myFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        image = wx.Image(r"C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\nicoDL_dev\nicoDL\data\thumbnail\16170998.jpeg")
        self.bitmap = image.ConvertToBitmap()

        wx.StaticBitmap(self, -1, self.bitmap, (0,0), self.GetClientSize())
        self.SetSize(image.GetSize())

app = wx.App(False)
frame = myFrame(None, "Image Viewer")
frame.Show()
app.MainLoop()


# coding: utf-8
import wx
class myFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        image = wx.Image(r"C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\nicoDL_dev\nicoDL\data\thumbnail\16170998.jpeg")
        self.bitmap = image.ConvertToBitmap()

        #self.SetSize(image.GetSize())

    def OnPaint(self, event=None):
        deviceContext = wx.PaintDC(self)
        deviceContext.Clear()
        deviceContext.SetPen(wx.Pen(wx.BLACK, 4))
        deviceContext.DrawBitmap(self.bitmap, 0, 0, True)

app = wx.App(False)
frame = myFrame(None, "Image Viewer")
frame.Show()
app.MainLoop()

# coding: utf-8

import wx


class panel1(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        a = u"ボーマス18 B06参加します！ sm16150525 ゆきめぐさんのイラストからイメージして曲を作りました ボマス18で頒布する\nWhiteMoon BlackMoonからの ぐみくー和風曲を別アレンジ版にしました アルバム収録版は..."
        # 画像
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        image = wx.Image(r"C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\nicoDL_dev\nicoDL\data\thumbnail\3262156.jpeg")
        self.bitmap = image.ConvertToBitmap()


        self.mess_st = wx.StaticText(self, -1, u'ダウンロード中')
        self.movie_id_st = wx.StaticText(self, -1, 'sm99999999')
        self.name_st = wx.StaticText(self, -1, 'name')
        self.option_st = wx.StaticText(self, -1, 'options: options')

        #self.thumbnail_panel = nicodl_thumbnailPanel(parent, r"C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\nicoDL_dev\nicoDL\data\thumbnail\3262156.jpeg")
        self.description = wx.TextCtrl(self,-1, a, size=(200, 100), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)

        # sizer
        sizer = wx.GridBagSizer(2,6)


        #
        sizer2.Add(self.bitmap.GetSize())
        sizer2.Add(self.movie_id_st)
        sizer3.Add(self.mess_st)
        sizer3.Add(self.name_st)
        sizer3.Add(self.description)
        sizer3.Add(self.option_st)
        sizer1.Add(sizer2, proportion=1,flag=wx.EXPAND|wx.ALL, border=10)
        sizer1.Add(sizer3)
        self.SetSizerAndFit(sizer1)

    def OnPaint(self, event=None):
        deviceContext = wx.PaintDC(self)
        deviceContext.Clear()
        deviceContext.SetPen(wx.Pen(wx.BLACK, 4))
        deviceContext.DrawBitmap(self.bitmap, 10, 10, True)


class mainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)

        panel1(self)



app = wx.App(False)
frame = mainWindow(None, "Image Viewer")
frame.Show()
app.MainLoop()
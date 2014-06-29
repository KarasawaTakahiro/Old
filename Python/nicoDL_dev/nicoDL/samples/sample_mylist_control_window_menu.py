#-*- coding: utf-8 -*-

import wx

class Example(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(Example, self).__init__(*args, **kwargs)
        p = wx.Panel(self)
        self.thumbnailfile=r"C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\nicoDL_dev\nicoDL\data\thumbnail\3262156.jpeg"
        bmp = wx.Bitmap(self.thumbnailfile, wx.wx.BITMAP_TYPE_JPEG)
        self.thumbnail = wx.StaticBitmap(p, -1, bmp)
        sizer=wx.GridBagSizer(3,3)
        sizer.Add(self.thumbnail,(2,2),flag=wx.EXPAND)
        p.SetSizerAndFit(sizer)


        self.InitUI()

    def InitUI(self):

        menubar = wx.MenuBar()  # 繝｡繝九Η繝ｼ繝舌・
        fileMenu = wx.Menu()  # 繝｡繝九Η繝ｼ
        fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application') # menu item
        menubar.Append(fileMenu, '&File')  # menubar append
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)

        self.SetSize((300, 200))
        self.SetTitle('Simple menu')
        self.Centre()
        self.Show(True)

    def OnQuit(self, e):
        self.Close()

def main():

    ex = wx.App()
    Example(None)
    ex.MainLoop()


if __name__ == '__main__':
    main()
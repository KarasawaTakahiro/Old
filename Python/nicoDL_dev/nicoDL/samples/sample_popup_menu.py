#-*- coding: utf-8 -*-


import wx

class MyApp(wx.PySimpleApp):
    def OnInit(self):
        self.frm = wx.Frame(None, -1, 'Title', size=(300,200))
        self.p = p = wx.Panel(self.frm, -1)

        self.p.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightUp) # for wxMSW
        self.p.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)            # for wxGTK
        self.frm.Show()
        return True

    def OnRightUp(self, event):
        if not hasattr(self, "popupID1"): # 起動後、一度だけ定義する。
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()

            self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
            self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)

        menu = wx.Menu()
        menu.Append(self.popupID1, "Do something")
        menu.Append(self.popupID2, "Quit")

        self.p.PopupMenu(menu)
        menu.Destroy()

    def OnPopupOne(self, event):
        print 'Do something'

    def OnPopupTwo(self, event):
        print 'Application will quit.'
        self.frm.Close()

app = MyApp()
app.MainLoop()
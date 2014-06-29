#!/usr/bin/env python
#-*- coding: utf-8 -*-

import pickle
import wx

class nicoDL_mainWindow(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is a main object", (20,20))

class nicoDL_mylistWindow(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is a mylist object", (20,20))

class nicoDL_setupWindow(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.load()  # 初期値決定

        # text
        gmail_ID_t = wx.StaticText(self, -1, "Gmail ID")
        gmail_PW_t = wx.StaticText(self, -1, "Gmail PW")
        nico_ID_t = wx.StaticText(self, -1, u"ニコニコ動画ID")
        nico_PW_t = wx.StaticText(self, -1, u"ニコニコ動画PW")
        to_addr_t = wx.StaticText(self, -1, u"完了メール送信先アドレス")
        savedir_t = wx.StaticText(self, -1, u"動画保存フォルダ")

        # Save Button
        save_button = wx.Button(self, -1, label=u'保存')

        # Choose Directory
        savedir_button = wx.Button(self, -1, label=u"フォルダを選択")

        # TextControls
        gmail_ID_tc = wx.TextCtrl(self, -1, value=self.gmail_ID_pre)
        gmail_PW_tc = wx.TextCtrl(self, -1, value=self.gmail_PW_pre, style=wx.TE_PASSWORD)
        nico_ID_tc = wx.TextCtrl(self, -1, value=self.nico_ID_pre)
        nico_PW_tc = wx.TextCtrl(self, -1, value=self.nico_PW_pre, style=wx.TE_PASSWORD)
        to_addr_tc = wx.TextCtrl(self, -1, value=self.to_addr_pre)
        self.savedir_tc = wx.TextCtrl(self, -1, value=self.savedir_pre, style=wx.TE_READONLY)

        # Bind
        self.Bind(wx.EVT_TEXT, self.TextControl_Gmail_ID, gmail_ID_tc)
        self.Bind(wx.EVT_TEXT, self.TextControl_Gmail_PW, gmail_PW_tc)
        self.Bind(wx.EVT_TEXT, self.TextControl_Nico_ID, nico_ID_tc)
        self.Bind(wx.EVT_TEXT, self.TextControl_Nico_PW, nico_PW_tc)
        self.Bind(wx.EVT_TEXT, self.TextControl_To_Addr, to_addr_tc)
        self.Bind(wx.EVT_BUTTON, self.Button_Savedir_Evt, savedir_button)
        self.Bind(wx.EVT_BUTTON, self.save, save_button)

        # panel
        dummy_panel_1 = wx.Panel(self, -1)
        dummy_panel_2 = wx.Panel(self, -1)
        dummy_panel_3 = wx.Panel(self, -1)
        dummy_panel_4 = wx.Panel(self, -1)
        dummy_panel_5 = wx.Panel(self, -1)
        dummy_panel_6 = wx.Panel(self, -1)
        dummy_panel_7 = wx.Panel(self, -1)

        # sizer
        layout = wx.GridSizer(7,3)
        layout.Add(gmail_ID_t, flag=wx.ALIGN_CENTRE)
        layout.Add(gmail_ID_tc, flag=wx.ALIGN_CENTRE)
        layout.Add(dummy_panel_1)
        layout.Add(gmail_PW_t, flag=wx.ALIGN_CENTRE)
        layout.Add(gmail_PW_tc, flag=wx.ALIGN_CENTRE)
        layout.Add(dummy_panel_2)
        layout.Add(nico_ID_t, flag=wx.ALIGN_CENTRE)
        layout.Add(nico_ID_tc, flag=wx.ALIGN_CENTRE)
        layout.Add(dummy_panel_3)
        layout.Add(nico_PW_t, flag=wx.ALIGN_CENTRE)
        layout.Add(nico_PW_tc, flag=wx.ALIGN_CENTRE)
        layout.Add(dummy_panel_4)
        layout.Add(to_addr_t, flag=wx.ALIGN_CENTRE)
        layout.Add(to_addr_tc, flag=wx.ALIGN_CENTRE)
        layout.Add(dummy_panel_5)
        layout.Add(savedir_t, flag=wx.ALIGN_CENTRE)
        layout.Add(self.savedir_tc, flag=wx.ALIGN_CENTRE)
        layout.Add(savedir_button, flag=wx.ALIGN_CENTRE)
        layout.Add(dummy_panel_6)
        layout.Add(dummy_panel_7)
        layout.Add(save_button, flag=wx.ALIGN_RIGHT)
        self.SetSizer(layout)


    def load(self):
        """
        データの読み込み
        """
        try:
            f = open("test\info.ndl")
            info = pickle.load(f)
            f.close()
            self.gmail_ID = self.gmail_ID_pre = info["gmail_ID"]
            self.gmail_PW = self.gmail_PW_pre = info["gmail_PW"]
            self.nico_ID = self.nico_ID_pre = info["nico_ID"]
            self.nico_PW = self.nico_PW_pre = info["nico_PW"]
            self.to_addr = self.to_addr_pre = info["to_addr"]
            self.savedir = self.savedir_pre = info["savedir"]
        except IOError:
            print u"info 初期化"
            self.gmail_ID = self.gmail_ID_pre = u""
            self.gmail_PW = self.gmail_PW_pre = u""
            self.nico_ID = self.nico_ID_pre = u""
            self.nico_PW = self.nico_PW_pre = u""
            self.to_addr = self.to_addr_pre = u""
            self.savedir = self.savedir_pre = u""

    def save(self, evt):
        """
        データの保存
        """
        self.gmail_ID = self.gmail_ID_pre
        self.gmail_PW = self.gmail_PW_pre
        self.nico_ID = self.nico_ID_pre
        self.nico_PW = self.nico_PW_pre
        self.to_addr = self.to_addr_pre
        self.savedir = self.savedir_pre

        info = {
                "gmail_ID":self.gmail_ID,
                "gmail_PW":self.gmail_PW,
                "nico_ID":self.nico_ID,
                "nico_PW":self.nico_PW,
                "to_addr":self.to_addr,
                "savedir":self.savedir,
                }
        print info
        try:
            f = open("test\info.ndl", "w")
            pickle.dump(info, f)
        finally:
            f.close()

    def Button_Savedir_Evt(self, evt):
        """
        フォルダ取得
        """
        savedir_dd = wx.DirDialog(self, defaultPath=self.savedir_pre)
        if savedir_dd.ShowModal() == wx.ID_OK:
            self.savedir_pre = savedir_dd.GetPath()
        savedir_dd.Destroy()
        self.savedir_tc.WriteText(self.savedir_pre)
        print self.savedir_pre

    def TextControl_Gmail_ID(self, evt):
        """
        Gmail ID 取得
        """
        tc = evt.GetEventObject()
        self.gmail_ID_pre = tc.GetValue()
        print self.gmail_ID_pre

    def TextControl_Gmail_PW(self, evt):
        """
        Gmail PW 取得
        """
        tc = evt.GetEventObject()
        self.gmail_PW_pre = tc.GetValue()
        print self.gmail_PW_pre

    def TextControl_Nico_ID(self, evt):
        """
        ニコニコ動画 ID 取得
        """
        tc = evt.GetEventObject()
        self.nico_ID_pre = tc.GetValue()
        print self.nico_ID_pre

    def TextControl_Nico_PW(self, evt):
        """
        ニコニコ動画 PW 取得
        """
        tc = evt.GetEventObject()
        self.nico_PW_pre = tc.GetValue()
        print self.nico_PW_pre

    def TextControl_To_Addr(self, evt):
        """
        通知メール送信先 取得
        """
        tc = evt.GetEventObject()
        self.to_addr_pre = tc.GetValue()
        print self.to_addr_pre

class nicoDL(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, None, title="nicoDL")

        # ICON
        self.tb_ico = wx.TaskBarIcon()
        self.ico = wx.Icon("data\\nicodl.ico", wx.BITMAP_TYPE_ICO)
        self.tb_ico.SetIcon(self.ico, u"nicoDL is runnnig!!")

        # Bind
        self.tb_ico.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.OnRightUp)
        #self.tb_ico.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.MessageInfo)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        #create Panel and a notebook on the panel
        panel = wx.Panel(self)
        notebook = wx.Notebook(panel)

        # create the page windows
        win_main = nicoDL_mainWindow(notebook)
        win_mylist = nicoDL_mylistWindow(notebook)
        win_setup = nicoDL_setupWindow(notebook)

        # add the pages
        notebook.AddPage(win_main, u'メイン')
        notebook.AddPage(win_mylist, 'win_mylist')
        notebook.AddPage(win_setup, u'設定')

        # put the notebook in a sizer for the panel to manage the layout
        sizer = wx.BoxSizer()
        sizer.Add(notebook, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        #self.Show()

    # Taskbar
    def OnRightUp(self, event):
        if not hasattr(self, "popupID1"):  # 起動後、一度だけ定義する。
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()

            self.tb_ico.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1) # Bind 先が icon なのがミソ
            self.tb_ico.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
        # メニュー作成
        menu = wx.Menu()
        menu.Append(self.popupID1, u"ウィンドウを表示")
        menu.AppendSeparator()
        menu.Append(self.popupID2, u"終了")

        self.tb_ico.PopupMenu(menu)
        menu.Destroy()

    def OnPopupOne(self, evt):
        print 'OnPopupOne'
        self.Show()

    def OnPopupTwo(self, evt):
        print 'OnPopupTwo'
        self.OnExitApp(None)
    # Taskbar ココまで

    def OnClose(self, evt):
        """
        バツ押したとき
        """
        print "CloseEvent"
        self.OnExitApp()

    def OnExitApp(self, evt=None):
        """
        終了処理
        """
        self.tb_ico.Destroy()
        self.Destroy()


if __name__ == '__main__':
    app = wx.App()
    nicodl = nicoDL()
    app.MainLoop()
    """app = wx.App()
    nicodl = nicoDL(None, -1, u"nicoDL.exe")
    nicodl.Show()
    app.MainLoop()"""





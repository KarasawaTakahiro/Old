#!/usr/bin/env python
#-*- coding: utf-8 -*-

import nicodl_main_gui_thread as nicodl_main
import os
import pickle
import sys
import wx


#ユーザー設定部
try:
    f = open('info.ndl')
except IOError:
    print u'まず nicoDL_setup.exe を実行してください。'
    sys.exit()
info = pickle.load(f)
f.close()

directory = os.getcwd() #ur'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\nicoDL'
user_id = info['NICO_ID'] #'zeuth717@gmail.com'  # ニコニコアカウント
pass_wd = info['NICO_PW'] #'kusounkobaka'  # ニコニコパス
base_save_dir = info['SAVE_DIR'][1] #r'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\Temporary Files'
save_dir = info['SAVE_DIR'][0] #r'E:\Takahiro\movie'



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        print 'Start!'
        self.debug = False

        # ICON
        self.tb_ico = wx.TaskBarIcon()
        self.ico = wx.Icon("nicodl.ico", wx.BITMAP_TYPE_ICO)
        self.tb_ico.SetIcon(self.ico, u"nicoDL is runnnig!!")

        # Bind
        self.tb_ico.Bind(wx.EVT_TASKBAR_RIGHT_DCLICK,self.OnClick)
        self.tb_ico.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.MessageInfo)

        #
        try:
            self.nicodl = nicodl_main.RemoteNicovideoDL(directory, user_id, pass_wd, save_dir, base_save_dir, debug=self.debug)
            self.nicodl.start()
        except StandardError, mess:
            self.RaiseError(mess)
            wx.Exit()

        #self.end()

    # Message
    def MessageInfo(self, evt):
        print 'Mess'
        mess = self.nicodl.message
        dial = wx.MessageDialog(None, mess, 'Info', wx.OK)
        dial.ShowModal()

    def OnClick(self, evt):
        #self.tb_ico.PopupMenu(MyPopupMenu(self))  # 例についてた
        print 'End'
        self.tb_ico.RemoveIcon()
        wx.Exit()

    def RaiseError(self, errormess):
        print '!RaiseError!'
        mess = u'An error occurred.\nYou can copy and paste in "Ctrl+C".\n\n"%s"' % str(errormess).encode('utf-8')
        dial = wx.MessageDialog(None, mess, 'Exclamation', wx.OK | wx.ICON_EXCLAMATION)
        dial.ShowModal()
        #wx.Exit()  #どこに付けるべきか

    def end(self):
        if self.nicodl.flag_end:
            wx.Exit()


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(None, -1, 'nicoDL.py')
    app.MainLoop()
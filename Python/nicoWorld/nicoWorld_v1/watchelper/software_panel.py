
# coding: utf8
"""
created on 2012/05/09
created by KarasawaTakahiro
"""

import os
import sys
import wx

class software_panel(wx.Panel):
    """
    *メッセージ
    *ラジオボタン
    *登録ボタン
    *選択されているソフトを返す関数
    * self.setected_software に選択されたソフトのフルパスが入っている
    """
    def __init__(self, cwd=os.getcwd(), softwares=[], *args, **kw):
        wx.Panel.__init__(self, *args, **kw)

        self.cwd = cwd
        self.softwares = []
        self.selected_software = None

        self.softwares.extend(softwares)

        self.sbox = wx.StaticBox(self)
        self.st = wx.StaticText(self,)
        self.btn = wx.Button(self, label=u'新規登録')
        # ラジオボタンをリストを入れておく, sizer用
        self.rbtns = [wx.RadioButton(self, label=os.path.split(exe)[-1]) for exe in self.softwares]

        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.sizer1 = wx.StaticBoxSizer(self.sbox, wx.VERTICAL)
        self.sizer1.Add(wx.StaticText(self, label=u'登録済みソフト'), 0, wx.EXPAND)
        for item in self.rbtns:
            self.sizer1.Add(item, 0, wx.EXPAND)
        self.sizer0.Add(self.sizer1, 1, wx.EXPAND)
        self.sizer0.Add(self.btn, 0, wx.ALIGN_LEFT)#wx.EXPAND)
        #self.SetSizerAndFit(self.sizer0)
        
        self.BindRadioButton()
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.btn)
        
    def getSoftware(self):
        if not(self.selected_software == None):
            return self.selected_software
        else:
            return False
    def getSoftwareAll(self):
        return self.softwares

    def OnRadioButton(self, evt):
        """ラジオボタンが選択されたとき"""
        radio_selected = evt.GetEventObject()
        for item in self.softwares:
            if os.path.split(item)[-1] == radio_selected.GetLabel():
                self.selected_software = item
                break
        else:
            # ヒットしなかった
            return False

    def OnButton(self, evt):
        #wildcard = u'動画再生可能ソフト(*.exe)|*.exe'
        try:
            dlg = wx.FileDialog(self, message=u'選択してください。',
                defaultDir=os.getcwd(),
                wildcard=u'動画再生可能ソフト(*.exe)|*.exe',#wildcard,
                style=wx.OPEN|wx.CHANGE_DIR)
        except UnicodeDecodeError:
            dlg = wx.FileDialog(self, message=u'選択してください。',
                defaultDir=self.cwd,
                wildcard=u'動画再生可能ソフト(*.exe)|*.exe',#wildcard,
                style=wx.OPEN|wx.CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            getpath = dlg.GetPath()
            if not(type(getpath) == unicode):
                #デコード
                getpath = getpath.decode(sys.getfilesystemencoding())
            # item: .exeのフルパス <type 'unicode'>
            self.AppendSoftware(getpath)
        dlg.Destroy()

    def AppendSoftware(self, exe):
        """ソフトを追加
        exe: 追加するソフトのフルパス"""
        if self.checkOverlap(self.softwares, exe):
            #print 'no overlap'
            self.softwares.append(exe)
            rb = wx.RadioButton(self, label=os.path.split(exe)[-1])
            self.rbtns.append(rb)
            self.sizer1.Add(rb, 0, wx.EXPAND)
            self.Layout()
            self.BindRadioButton()
        else:
            # 被った
            #pass
            print 'overlap'

    def BindRadioButton(self):
        """ラジオボタンのバインド"""
        for item in self.rbtns:  self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton, item)

    def checkOverlap(self, items, item):
        """
        items: list
        item: 追加したい
        *リストを渡す
        *かぶらなかればTrue
        *被ればFalse
        *それ以外None
        """
        
        try:
            items.index(item)
            return False
        except ValueError:
            return True

class MainWin(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        software_panel(self)


if __name__ == '__main__':
    app = wx.App(redirect=False)
    win = MainWin(parent=None)
    win.Show()
    app.MainLoop()

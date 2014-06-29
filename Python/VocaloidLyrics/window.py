# coding: utf-8

import wx

class MyList(wx.ListCtrl):
    def __init__(self, parent, style=wx.LC_REPORT, *args, **kwargs):
        wx.ListCtrl.__init__(self, parent, style=style, *args, **kwargs)
        self.InsertColumn(0, u"曲名")
        self.InsertColumn(1, u"URL")
        self.SetColumnWidth(0, 300)
        self.SetColumnWidth(1, 200)

class VocaloidLyricsWindow(wx.Frame):
    def __init__(self, title, *args, **kwargs):
        wx.Frame.__init__(self, None, title=title, *args, **kwargs)
        panel = wx.Panel(self)
        self.btnSearch = wx.Button(panel, -1, label=u'検索')
        self.searchbox = wx.TextCtrl(panel, -1, style=wx.TE_PROCESS_ENTER)
        self.listctrl = MyList(panel, size=self.GetSizeTuple())
        self.stInfo = wx.StaticText(panel)
        self.toaddrbox = wx.TextCtrl(panel, -1, u"ここにメールアドレスを入力して送信ボタンを押す", style=wx.TE_PROCESS_ENTER)
        self.btnSendMail = wx.Button(panel, label=u'送信')

        self.btnSearch.SetToolTipString(u"検索ワードを入力してからこのボタンを押す")
        self.searchbox.SetToolTipString(u"ここに検索ワードを入力します")
        self.listctrl.SetToolTipString(u"検索結果が一覧表示されます")
        self.stInfo.SetToolTipString(u"いろいろな情報が表示されます")
        self.toaddrbox.SetToolTipString(u"歌詞を送信する相手を入力します")
        self.btnSendMail.SetToolTipString(u"歌詞の送信先を入力したら押します")

        sizer0 = wx.BoxSizer(wx.VERTICAL)
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizerMail = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.searchbox, 1, wx.EXPAND, )
        sizer1.Add(self.btnSearch, 0, wx.EXPAND)
        sizerMail.Add(self.toaddrbox, 1, wx.EXPAND)
        sizerMail.Add(self.btnSendMail, 0, wx.EXPAND)
        sizer0.Add(self.stInfo, 0, border=2, flag=wx.EXPAND|wx.EAST|wx.WEST)
        sizer0.Add(sizer1, 0, wx.EXPAND)
        sizer0.Add(self.listctrl, 1,  wx.EXPAND)
        sizer0.Add(sizerMail, 0, wx.EXPAND | wx.NORTH, border=3)
        panel.SetSizerAndFit(sizer0)

        self._Data = {}

        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSize(self, evt):
        print self.GetSize()
        evt.Skip()

    def AppendItem(self, *labels):
        """
        新しく行を追加する
        labalsに渡した順でラベルを追加していく
        labels[1]をデータとして保存
        """
        num = len(self._Data)
        self._Data.update({num:labels})
        index = self.listctrl.InsertStringItem(self.listctrl.GetItemCount(), labels[0])
        for count in xrange(1, len(labels)):
            self.listctrl.SetStringItem(index, col=count, label=labels[count])
        self.listctrl.SetItemData(index, num)

    def GetItemCount(self):
        return self.listctrl.GetItemCount()

    def GetSelectedItemCount(self):
        return self.listctrl.GetSelectedItemCount()

    def GetFirstSelected(self):
        return self.listctrl.GetFirstSelected()

    def GetNextSelected(self, item):
        return self.listctrl.GetNextSelected(item)

    def GetData(self, index):
        return self._Data[index]

    def GetToaddr(self):
        return self.toaddrbox.GetValue()

    def ListClear(self):
        """リセット"""
        self.listctrl.DeleteAllItems()
        self._Data = {}

    def setInfo(self, text):
        self.stInfo.SetLabel(text)

    def setSearchWord(self, word):
        self.searchbox.SetLabel(word)

    def setFocusSearchbox(self):
        self.searchbox.SetFocus()

    def isEmpty(self):
        """
        self.searchboxが空ならTrue
        """
        print self.searchbox.GetValue()
        if self.searchbox.GetValue() == u"":
            return True
        else:
            return False

    def setToaddrLabel(self, text):
        self.toaddrbox.SetValue(text)

    def doInformation(self, caption, message):
        """
        メッセージダイアログを表示
        """
        dlg = wx.MessageDialog(self, caption, message, wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

class PrevWindow(wx.Frame):
    def __init__(self, parent, *args, **kwargs):
        wx.Frame.__init__(self, parent, *args, **kwargs)
        self.tc = wx.TextCtrl(self, -1,  style=wx.TE_MULTILINE| wx.TE_READONLY)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tc, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def clear(self):
        self.tc.Clear()

    def writeText(self, text):
        """
        テキストを書く
        """
        self.tc.Clear()
        self.tc.WriteText(text)

    def addedText(self, text):
        """
        テキストを追記していく
        """
        self.tc.WriteText(text)

    def setInsertionPoint(self, pos):
        self.tc.SetInsertionPoint(pos)

    def Focus(self):
        self.tc.SetFocus()

    def OnClose(self, evt):
        self.Hide()


if __name__ == '__main__':
    app = wx.App(False)
    frame = VocaloidLyricsWindow(title='VocaloidLirycs')
    frame.Show()
    app.MainLoop()

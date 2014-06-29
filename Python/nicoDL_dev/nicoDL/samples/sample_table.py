#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import wx.lib.mixins.listctrl as listmix
#import amazon as az
import sys

# 検索結果表示リスト
class BookList(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)


# フレーム
class AmazonBookSearchFrameWx(wx.Frame):

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(750, 300))

        # パネル
        panel = wx.Panel(self, -1)

        # 入力
        self.text = wx.TextCtrl(panel, 2, "ここにタイトル入力！", size = (250, 30))
        self.text.Bind(wx.EVT_SET_FOCUS, self.textClear, id = self.text.GetId())
        # ボタン
        self.button = wx.Button(panel, 1, "検索")
        self.button.Bind(wx.EVT_BUTTON, self.submit, id = self.button.GetId())

        # リスト
        self.list = BookList(self, 3, size = (730, 200)
                             ,style=wx.LC_REPORT
                             | wx.LC_SORT_ASCENDING
                             | wx.LC_SINGLE_SEL
                             )
        self.__init_book_list()

        # レイアウト
        gbs = wx.GridBagSizer(2, 2)
        gbs.Add(self.text, (0,0))
        gbs.Add(self.button, (0,1))
        gbs.Add(self.list, (1,0), (1, 2))

        box = wx.BoxSizer()
        box.Add(gbs, 0, wx.ALL, 10)
        panel.SetSizerAndFit(box)


        self.Centre()
        self.Show(True)

    def __init_book_list(self):
        # リストの初期化
        self.list.InsertColumn(0, "タイトル", wx.LIST_FORMAT_CENTER)
        self.list.InsertColumn(1, "著者", wx.LIST_FORMAT_CENTER)
        self.list.InsertColumn(2, "レビュー", wx.LIST_FORMAT_CENTER)

        self.list.SetColumnWidth(0, 500)
        self.list.SetColumnWidth(1, 100)
        self.list.SetColumnWidth(2, 20)

    def submit(self, event):
        # 前の検索結果削除
        self.list.DeleteAllItems()

        param = {az.AmazonClient.TITLE: self.text.GetValue()}
        client = az.AmazonClient(param)
        bookList = client.doRequest()

        for book in bookList:
            index = self.list.InsertStringItem(sys.maxint, book.title)
            self.list.SetStringItem(index, 1, book.author)
            self.list.SetStringItem(index, 2, str(book.averagerating))

    def textClear(self, event):
        self.text.SetValue("")


if __name__ == "__main__":
    app = wx.App()
    AmazonBookSearchFrameWx(None, -1, '本の検索')
    app.MainLoop()

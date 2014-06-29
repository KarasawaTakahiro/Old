# !/usr/bin/env python
# coding: utf-8

import gmailManage as gmail
import os
import sys
import threading
import vocaloid_lyrics_search as VocaloidLyricsSearch
import window
import wx

class Main(window.VocaloidLyricsWindow):
    def __init__(self, title):
        window.VocaloidLyricsWindow.__init__(self, title=title, size=(520, 490))
        self.prevWin = window.PrevWindow(self, )
        self.prevWin.SetSize((700,650))
        self.VL = VocaloidLyricsSearch.VocaloidLyrics()
        self.cdir = os.getcwd()
        self.timer = wx.Timer(self, -1)

        self.saveDir = self.cdir  # 設定関数で定義

        self.listActivateId = wx.NewId()

        self.Bind(wx.EVT_BUTTON, self.OnBtnSearch, self.btnSearch)
        #self.Bind(wx.EVT_BUTTON, self.OnBtnSave, self.btnSave)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListActivated, self.listctrl, id=self.listActivateId)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnBtnSearch, self.searchbox)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnBtnSendMail, self.toaddrbox)
        self.Bind(wx.EVT_BUTTON, self.OnBtnSendMail, self.btnSendMail)
        self.Bind(wx.EVT_TIMER, self.OnTimer)

        self.setFocusSearchbox()
        self.initInfo()
        self.timer.Start(6000000)  # 10分

    def OnTimer(self, evt):
        print 'Reset'
        self.initInfo()

    def OnBtnSearch(self, evt):
        if self.isEmpty(): return
        self.btnSearch.Disable()  # self.search() 内で有効化
        self.ListClear()
        th = threading.Thread(target=self.search)
        th.daemon = True
        th.start()

    def OnBtnSave(self,evt):
        """
        セーブボタンを押した
        """
        self.btnSave.Disable()  # self.saveFile()　内で有効化
        th = threading.Thread(target=self.saveFile)
        th.daemon = True
        th.start()
        print "OnSaveBtn"

    def OnBtnSendMail(self, evt):
        """
        メール送信ボタンを押した
        """
        toaddr = self.GetToaddr()
        if len(self.getSelects()) == 0:
            print "disselected"
            self.setInfo(u"歌詞を取得したい曲名を選択してください")
            self.doInformation(u"歌詞を取得したい曲名を選択してください", "Vocaloid Lyrics")
            return
        elif toaddr == "" or toaddr == u"ここにメールアドレスを入力して送信ボタンを押す":
            self.setInfo(u"送信先を入力してください")
            self.doInformation(u"送信先を入力してください", "Vocaloid Lyrics")
            return
        for title, url in self.getSelects():
            lyrics = self.VL.getlyrics(url)
            body = lyrics
            subject = title
            th = threading.Thread(target=self.sendLyrics, args=[toaddr, subject, body])
            th.daemon = True
            th.start()

    def OnListActivated(self, evt):
        self.Unbind(wx.EVT_LIST_ITEM_ACTIVATED, id=self.listActivateId)  # self.showPreview()内でバインド
        self.setInfo(u"歌詞をプレビュー表示します! 何も表示されなかったらごめんね")
        th = threading.Thread(target=self.showPreview)
        th.daemon = True
        th.start()
        
    def initInfo(self):
        self.setInfo(u"↓のボックスに検索ワードを入れて検索ボタンをクリック!")
        self.setToaddrLabel(u"ここにメールアドレスを入力して送信ボタンを押す")
        self.toaddrbox.SelectAll()
        self.setSearchWord(u"")
        self.ListClear()

    def search(self):
       keyword = self.searchbox.GetValue()
       self.setInfo(u"検索中...")
       for item in self.VL.search(keyword):
           self.AppendItem(item[0], item[1])
       self.setInfo(u"検索完了! 保存したい曲を選択して保存ボタンをクリック! 曲名をダブルクリックするとプレビュー表示します!")
       self.btnSearch.Enable()

    def getSelects(self):
        """
        選択されているものをリストで返す
        """
        selectedList = []
        selected = self.GetFirstSelected()
        if selected == -1:
            # 選択されていない
            pass
        else:
            item = self.GetData(selected)
            title = item[0]
            url = item[1]
            selectedList.append((title, url))
            for count in xrange(self.GetSelectedItemCount() - 1):
                item = self.GetData(self.GetNextSelected(selected + 1))
                title = item[0]
                url = item[1]
                selectedList.append((title, url))
        return selectedList

    def saveFile(self):
        """
        選択されたものをすべて保存
        """
        selected = self.GetFirstSelected()
        if selected == -1:
            # 選択されていない
            pass
        else:
            item = self.GetData(selected)
            title = item[0]
            url = item[1]
            path = self.saveLyrics(title, url)
            print path
            self.setInfo(path)
            for count in xrange(self.GetSelectedItemCount() - 1):
                item = self.GetData(self.GetNextSelected(selected + 1))
                title = item[0]
                url = item[1]
                path = self.saveLyrics(title, url)
                print path
        self.btnSave.Enable()

    def saveLyrics(self, title,  url):
        self.setInfo(u"".join([u'"', title, u'"を保存します。']))
        lyrics = self.VL.getlyrics(url)
        path = os.path.join(self.saveDir, "%s.txt" % title)
        f = open(path, "w")
        f.write(lyrics.encode('utf-8'))
        f.close()
        self.setInfo("".join(['"', title, u'"を保存しました。']))
        return path

    def sendLyrics(self, toaddr, title, body):
        self.btnSendMail.Disable()  # self.sendLyrics()で有効化
        self.setInfo(u"".join([u'"', title, u'"を送信します。']))
        mail = gmail.Gmail("vocaloidlyrics717@gmail.com", "vocaloidlyrics717")
        mail.createMessage(toaddr, title, body)
        mail.send()
        self.setInfo("".join(['"', toaddr, '"', u"宛てに", '"', title, u'"を送信しました。']))
        self.btnSendMail.Enable()

    def showPreview(self):
        self.prevWin.Show()
        item = self.GetData(self.GetFirstSelected())
        title = item[0]
        url = item[1]
        self.prevWin.SetTitle(title + u"～取得中～")
        self.prevWin.clear()
        for lyrics in self.VL.xgetlyrics(url):
            print lyrics
            self.prevWin.addedText(lyrics)
        self.prevWin.setInsertionPoint(0)
        self.prevWin.SetTitle(title + u"～取得完了～")
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListActivated, self.listctrl, self.listActivateId)

if __name__ == "__main__":
    app = wx.App(False)
    frame = Main("Vocaloid Lyrics")
    frame.Show()
    app.MainLoop()

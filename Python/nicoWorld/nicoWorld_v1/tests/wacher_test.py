
# coding: utf-8
"""
created on 2012/03/27
created by KarasawaTakahiro
"""

import modules.formats as formats
import os
import subprocess
import sys
import threading
import wx


class SelectExePanel(wx.Panel):
    """
    *間違えて追加した.exeを削除する方法 -> 右クリックメニューでどうにか
    *保存ファイルの形式変更によるload(),save()の仕様変更
    
    self.selected に選択した.exeのフルパスが入っている
    """
    def __init__(self, data, *args, **kwargs):
        """"""
        wx.Panel.__init__(self, *args, **kwargs)
        self.exes = data.softwares  # load()の戻り値がリスト型であるべき
        # 登録済みのexeファイルのパス
        self.seleced = data.lsoftware
        # 最後に選択された.exeのフルパスを格納
        self.rbtns = []
        # exeファイルのラジオボタンオブジェクト

        """Wigets"""
        self.parent = kwargs['parent']
        self.btn = wx.Button(self, label=u'新規登録')
        self.sbox = wx.StaticBox(self,)
        for item in self.exes:
            rbobj = wx.RadioButton(self, label=os.path.split(item)[-1])
            if item == self.seleced:
                rbobj.SetValue(True)
            self.rbtns.append(rbobj)

        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.sizer1 = wx.StaticBoxSizer(self.sbox, wx.VERTICAL)
        self.sizer1.Add(wx.StaticText(self, label=u'追加済みファイル一覧'))
        self.sizer1.Add(wx.StaticLine(self))
        for item in self.rbtns:
            self.sizer1.Add(item, 0, wx.ALIGN_LEFT)
        self.sizer0.Add(self.sizer1, 1, flag=wx.EXPAND|wx.WEST|wx.EAST, border=5)
        self.sizer0.Add(self.btn, 0, wx.ALIGN_LEFT)
        self.SetSizerAndFit(self.sizer0)

        self.Bind(wx.EVT_BUTTON, self.AddDialog, self.btn)
        for item in self.rbtns:
            self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton, item)

    def OnRadioButton(self, evt):
        radio_selected = evt.GetEventObject()
        for item in self.exes:
            if os.path.split(item)[-1] == radio_selected.GetLabel():
                self.seleced = item
        else:
            # ヒットしなかった
            return False

    def RBtnBind(self):
        """
        self.rbtnsのラジオボタンのバインド
        self.rbtnsに追加したら呼び出す
        """
        for item in self.rbtns:
            self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton, item)

    def mkRadioButton(self, data):
        """
        data: List
        """
        if not(type(data) == type([])):  raise ValueError, u'data must be List'

        for item in data:
            #print "exes:",self.exes
            if not(item in self.exes):
                #print "items:",item  ##################################
                #print "items:",type(item)  ##############################
                rbobj = wx.RadioButton(self, label=os.path.split(item)[-1])
                self.rbtns.append(rbobj)
                self.sizer1.Add(rbobj, 0, wx.ALIGN_LEFT)
                self.exes.append(item)  # 登録済みリストに追加
        self.RBtnBind()  # バインドし直す
        self.sizer0.Layout()
    
    def AddDialog(self, evt):
        wildcard = u'動画再生可能.exe(*.exe)|*.exe'
        cwd = os.getcwd()

        dlg = wx.FileDialog(self, message=u'選択してください。',
            defaultDir=cwd,
            wildcard=wildcard,
            style=wx.OPEN|wx.MULTIPLE|wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            for item in dlg.GetPaths():
                if not(type(item) == type(u'')):
                    #デコード
                    item = item.decode(sys.getfilesystemencoding())
                # item: .exeのフルパス <type 'unicode'>
                self.mkRadioButton([item])

        dlg.Destroy()
        os.chdir(cwd)


class SelectMoviePanel(wx.Panel):
    """
    *選択した動画のフルパスを得られるようにする
    """
    def __init__(self, data, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.formats = data
        self.data = data.folders
        # フォルダのフルパスとファイルのリスト
        #[{folder:r'c:\movie', file:[x.mp4,*.*], lastfile:u'x.mp4'}, {},{}]
        self.exts = data.exts
        # 拡張子フィルター
        for item in self.data:
            if item['folder'] == data.lfolder:
                self.selected_folder = item  # 最後に再生したファイル 終了時、ロード時に決定
                break
        else:
            self.selected_folder = {'folder':u'', 'files':[], 'lastfile':u''}
        #print 'lfolder:', self.selected_folder
        # 最後に選択していたフォルダ、ファイル
        # 選択されているフォルダ、ファイルも示す
        
        self.exe_panel = SelectExePanel(parent=self, data=data)
        self.folder_lb = wx.ListBox(self, style=wx.LB_SINGLE)
        self.addbtn = wx.Button(self, label=u'フォルダ追加')
        self.file_lb = wx.CheckListBox(self)

        """前回終了時の再現"""
        for item in self.data:
            path = item['folder']
            # フォルダ
            if path == self.selected_folder['folder']:
                selected_index = self.folder_lb.Append(os.path.split(path)[-1], path)
                self.folder_lb.SetSelection(selected_index)
                # ファイル
                for filename in item['files']:
                    index = self.file_lb.Append(filename)
                    if filename == item['lastfile']:
                        self.file_lb.SetSelection(index)
                        self.file_lb.Check(index)
                        self.selected_file_index = index
            else:
                self.folder_lb.Append(os.path.split(path)[-1], path)

        """sizer"""
        sizer0 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.folder_lb, 1, wx.EXPAND)
        sizer1.Add(self.addbtn, 0, wx.EXPAND)
        sizer0.Add(sizer1, 0, wx.EXPAND)
        sizer0.Add(self.file_lb, 1, wx.EXPAND)
        sizer2.Add(self.exe_panel, 0, wx.EXPAND)
        sizer2.Add(sizer0, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer2)
        """ """
        
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.addbtn)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnFolderListBoxDoubleClicked, self.folder_lb)
        self.Bind(wx.EVT_LISTBOX, self.OnFolderListBoxSingleClicked, self.folder_lb)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnFileListBoxDoubleClicked, self.file_lb)
        self.Bind(wx.EVT_LISTBOX, self.OnFileListBoxClicked, self.file_lb)

    def OnButton(self, evt):
        """
        *フォルダ追加ボタンが押されたとき
        """
        dlg = wx.DirDialog(self, u'動画が保存されているフォルダを選択', style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            newdata = self.formats.mkFoldersFormat(folder=dlg.GetPath())
        dlg.Destroy()
        self.AppendFolder(newdata)
        self.OnFolderListBoxDoubleClicked(evt=False, datadic=newdata)

    def OnFolderListBoxDoubleClicked(self, evt, datadic=False):
        """
        *リストボックスでフォルダがダブルクリックされたときに呼ばれる
        self.dataを更新 してから表示
        """
        if evt:
            for item in self.data:
                if item['folder'] == evt.GetClientData():
                    self.selected_folder = item
                    break
            print 'DoubleClicked folder:', self.selected_folder['folder']
        elif datadic:
            self.selected_folder = datadic
            print 'Add folder:', self.selected_folder['folder']

        # 動画一覧に表示
        for item in self.data:
            if item['folder'] == self.selected_folder['folder']:
                self.F5File(item)
                self.AppendFile(item)
                break
        self.checkcheck()

    def OnFolderListBoxSingleClicked(self, evt):
        """
        *リストボックスでフォルダ名がシングルクリックされたときに呼ばれる
        self.dataを更新 => ダブルクリックから
        """
        for item in self.data:
            if item['folder'] == evt.GetClientData():
                self.selected_folder = item
                break
        #print 'SingleClicked'
        print 'selected_folder:', self.selected_folder['folder']
        
        # 動画一覧に表示
        for item in self.data:
            if item['folder'] == self.selected_folder['folder']:
                self.AppendFile(item)
                break
        self.checkcheck()

    def OnFileListBoxDoubleClicked(self, evt):
        """
        self.file_lbでダブルクリックしたときに呼ばれる
        """
        #print 'OnFileListBoxDClicked'
        pass

    def OnFileListBoxClicked(self, evt):
        """
        self.file_lbで選択したときに呼ばれる
        """
        self.selected_file_index = evt.GetSelection()
        print 'OnFileListBoxSingleClicked: %s' % evt.GetString()

    def AppendFolder(self, data):
        """
        *リストボックスに内容を書き込む
        path: フォルダのフルパス
        self.dataの内容をself.folder_lbに追加
        *フォルダ追加ボタンが押されたときに呼ばれる
        """
        self.data.append(data)
        # リストの内容を全削除
        for retry in xrange(3):
            del retry
            try:
                for no in xrange(0, self.folder_lb.GetCount()):  self.folder_lb.Delete(no)
                break
            except:
                print u'AppendFolderでエラーが発生'
                continue
        # 内容を追加していく
        for item in self.data:
            path = item['folder']
            self.folder_lb.Append(os.path.split(path)[1], path)
        self.Layout()

    def AppendFile(self, datadic):
        """
        *リストボックスに内容を書き込む
        datadic: self.dataの中の辞書
        
        datadicの内容をself.file_lbに追加
        *self.folderのItemがダブルクリックで選択されたときに実行
        """
        # 削除
        for _ in xrange(0, self.file_lb.GetCount()):  
            self.file_lb.Delete(0)
        # 追加
        for item in datadic['files']:
            index = self.file_lb.Append(item)
            if item == datadic['lastfile']:
                self.file_lb.SetSelection(index)

        self.Layout()

    def PlayCurrent(self):
        enc = sys.getfilesystemencoding()

        filepath = os.path.join(self.selected_folder['folder'], self.selected_folder['files'][self.selected_file_index])
        if type(u'') == type(filepath):
            # エンコード
            filepath = filepath.encode(enc)

        exe = self.exe_panel.seleced
        if exe == u'':
            # 選択されていない
            raise ValueError, u'ソフトが選択されていません。'
        elif unicode == type(exe):
            # エンコード
            exe = exe.encode(enc)
        elif type('') == type(exe):
            # <type str>でエンコードし直す 念のため
            exe = exe.decode(enc).encode(enc)

        command = [exe, filepath]
        #print exe.decode(enc), filepath.decode(enc)  # decodeしていることに注意
        # subprocessをスレッドで開始
        th = threading.Thread(target=subprocess.call, kwargs={'args':command})
        th.start()
        # lastfileを登録
        self.selected_folder['lastfile'] = self.file_lb.GetString(self.selected_file_index)
        # チェックをつける
        self.checkcheck()
        # lastfileなどの変更を更新
        count = 0
        for item in self.data:
            if item['folder'] == self.selected_folder['folder']:
                self.data[count] = self.selected_folder
                break
            else: count += 1

    def PlayNext(self):
        if not hasattr(self, 'selected_file_index'):
            raise ValueError, u'ファイルが選択されていません。'
        index = self.selected_file_index + 1
        try:
            self.file_lb.Select(index)
        except wx._core.PyAssertionError:
            raise ValueError, u'リストの最後です。'
        self.selected_file_index = index
        self.PlayCurrent()

    def PlayPre(self):
        if not hasattr(self, 'selected_file_index'):
            raise ValueError, u'ファイルが選択されていません。'
        elif self.selected_file_index == 0:
            raise ValueError, u'リストの先頭です。'
        index = self.file_lb.GetChecked()[-1] - 1
        self.file_lb.Select(index)
        self.selected_file_index = index
        self.PlayCurrent()

    def F5File(self, datadic):
        """
        *ファイルを更新する
        datadic: self.data内の辞書
        """
        # datadicのあった場所
        index = self.data.index(datadic)
        # ファイルの検索
        for root, dirs, files in os.walk(datadic['folder'], topdown=False):
            if root != datadic['folder']:
                continue
            del root, dirs
        encoding = sys.getfilesystemencoding()
        will = []
        for item in files:
            if not(type(item) == type(u'')):
                item = item.decode(encoding)
            # 拡張子の判定
            if os.path.splitext(item)[1] in self.exts:
                will.append(item)
        # 追加 被ったものはスキップ
        datadic['files'] = will
        datadic['files'] = list(set(datadic['files']))
        datadic['files'].sort()
        # 上書き保存
        self.data[index] = datadic

    def checkcheck(self):
        
        for item in self.data:
            if item['folder'] == self.selected_folder['folder']:
                try:
                    index = self.selected_folder['files'].index(self.selected_folder['lastfile'])
                    # if節内が実行されたとき
                    self.file_lb.SetSelection(index)
                    self.file_lb.SetChecked([index])
                    self.selected_file_index = index
                    break
                except ValueError:  pass
                # 見つからなかったとき


class MainWin(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        
        SAVE_FILE = u'watcher.nco'
        self.FORMATS = formats.WatchelperFormat()
        self.FORMATS.DUMPFILE = SAVE_FILE
        self.FORMATS.load()

        self.CreateStatusBar()

        self.panel = wx.Panel(self)
        self.panel2 = SelectMoviePanel(parent=self.panel, data=self.FORMATS)

        self.btn_play = wx.Button(self.panel, label=u'再生')
        self.btn_next = wx.Button(self.panel, label=u'次を再生')
        self.btn_pre = wx.Button(self.panel, label=u'前を再生')

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.panel2, 1, wx.EXPAND)
        self.sizer0 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer0.Add(self.btn_pre, 1, border=1, flag=wx.WEST|wx.EAST)
        self.sizer0.Add(self.btn_play, 1, border=1, flag=wx.WEST|wx.EAST)
        self.sizer0.Add(self.btn_next, 1, border=1, flag=wx.WEST|wx.EAST)
        self.sizer1 = wx.BoxSizer(wx.VERTICAL)
        self.sizer1.Add(self.sizer0, 0, wx.EXPAND)
        self.sizer1.Add(self.sizer, 1, wx.EXPAND)
        self.panel.SetSizerAndFit(self.sizer1)
        
        self.Bind(wx.EVT_BUTTON, self.OnPlayButton, self.btn_play)
        self.Bind(wx.EVT_BUTTON, self.OnPlayNextButton, self.btn_next)
        self.Bind(wx.EVT_BUTTON, self.OnPlayPreButton, self.btn_pre)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnPlayButton(self, evt):
        try:
            self.panel2.PlayCurrent()
            self.SetStatusText(u'')
        except ValueError, mess:
            self.SetStatusText(str(mess))
        
    def OnPlayNextButton(self, evt):
        try:
            self.panel2.PlayNext()
            self.SetStatusText(u'')
        except ValueError, mess:
            self.SetStatusText(str(mess))
        
    def OnPlayPreButton(self, evt):
        try:
            self.panel2.PlayPre()
            self.SetStatusText(u'')
        except ValueError, mess:
            self.SetStatusText(str(mess))

    def OnClose(self, evt):
        self.SetStatusText(u'終了処理中')
        self.FORMATS.mkWatchelperFormat(softwares = self.panel2.exe_panel.exes,
                                        folders = self.panel2.data,
                                        lsoftware = self.panel2.exe_panel.seleced,
                                        lfolder = self.panel2.selected_folder['folder'],
                                        exts = self.panel2.exts)
        self.FORMATS.save()
        self.Destroy()


if __name__ == '__main__':
    app = wx.App(redirect=False)
    win = MainWin(parent=None)
    win.Show()
    app.MainLoop()

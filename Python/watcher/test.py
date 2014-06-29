
#coding: utf-8
'''
Created on 2012/03/17

@author: KarasawaTakahiro
'''

import os
import pickle
import subprocess
import sys
import threading
import wx

def load(path=os.getcwd(), name='test.dump'):
    try:
        ff = open(os.path.join(path, name))
        data = pickle.load(ff)
    finally:  ff.close()
    data.sort()
    return data

def save(data, path=os.getcwd(), name='test.dump', add=False):
    """
    data: <type List>
    add: 追記
    """
    fullpath = os.path.join(path,name)
    try:
        if add:  # 追記
            loaddata = load(path, name)
            loaddata.extend(data)
            loaddata.sort()
            data = loaddata;  del loaddata
        ff = open(fullpath, 'w')
        pickle.dump(data, ff)
    finally:  ff.close()

class TestPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.sysencodeing = sys.getfilesystemencoding()
        self.choices = []
        self.choices_full = []
        for item in load():
            self.choices.append(os.path.split(item)[-1])
            self.choices_full.append(item)
        self.rb = wx.RadioBox(self, label='Test', choices=self.choices, majorDimension=1, style=wx.RA_SPECIFY_COLS)

        self.btn = wx.Button(self, label='On', pos=(150,0))
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.btn)

    def OnButton(self, evt):
        com = []
        com.append(self.choices_full[self.rb.GetSelection()])
        # ファイルを読み込む
        for root, dirs, files in os.walk(r"C:\Users\KarasawaTakahiro\Videos\Minecraft", topdown=True):
            del dirs
            root = root.decode(self.sysencodeing)
            for ff in files:
                #print type(ff)
                # デコードしてunicodeに直す
                ff = ff.decode(self.sysencodeing)
                #print type(ff)
                #print
                if ff.find(u'.mp4')>0:
                    com.append(os.path.join(root, ff))
        
        comed = []
        for item in com:
            print item
            # systemfileencodingにエンコード
            comed.append(item.encode(self.sysencodeing))
        # subprocessをスレッドで開始
        th = threading.Thread(target=subprocess.call, kwargs={'args':comed})
        th.start()

class TestFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        
        self.panel = TestPanel(self)



if __name__ == '__main__':
    save([r"C:\Program Files (x86)\にこぷれ\にこぷれ.exe",])
    save([r"C:\Program Files (x86)\GRETECH\GomPlayer\GOM.EXE"], add=True)
    app = wx.App(redirect=False)
    win = TestFrame(None)
    win.Show()
    app.MainLoop()
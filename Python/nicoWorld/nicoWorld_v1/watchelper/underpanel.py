
#coding: utf-8
"""
created on 2012/05/09
created by KarasawaTakahiro
"""

import file_checklistctrl as FileCheckListCtrl
import folder_listctrl as FolderListCtrl
import software_panel as SoftwarePanel
import os.path
import wx

class UnderPanel(SoftwarePanel.software_panel):
    """SoftwarePanel was expanded to FileCheckListCtrl and FolderListCtrl"""
    def __init__(self, *args, **kwargs):
        SoftwarePanel.software_panel.__init__(self, *args, **kwargs)
        self.filectrl = FileCheckListCtrl.FileCheckListCtrl(parent=self)
        self.folderctrl = FolderListCtrl.FolderListCtrl(parent=self)
        self.folderbtn = wx.Button(self, label=u'Append Folder')

        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.folderctrl, 1, wx.EXPAND)
        sizer1.Add(self.folderbtn, 0, wx.EXPAND)
        sizer.Add(self.sizer0, 0, wx.EXPAND)
        sizer.Add(sizer1, 1, wx.EXPAND)
        sizer.Add(self.filectrl, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer)
        
    def ListCtrlAppendFolder(self, format):
        index = self.folderctrl.appendData(format)
        print format[format.keys()[0]]
        label = os.path.split(format.keys()[0])[-1]
        self.folderctrl.InsertStringItem(index, label=label)
    def CheckListCtrlAppendFile(self, format):
        index = self.filectrl.appendData(format)
        for folder in format[format.keys()[0]]['files']:
            self.filectrl.InsertStringItem(index, label=folder)

if __name__ == '__main__':
    class __MainWin(wx.Frame):
        def __init__(self, *args, **kw):
            wx.Frame.__init__(self, *args, **kw)
            self.panel = UnderPanel(parent=self)
            for index in xrange(30):
                self.panel.filectrl.Data.update({index:str(index)})
                self.panel.folderctrl.Data.update({index:str(index)})
            else:
                self.panel.filectrl.Load()
                self.panel.folderctrl.Load()
            
    app = wx.App(redirect=False)
    win = __MainWin(parent=None)
    win.Show()
    app.MainLoop()
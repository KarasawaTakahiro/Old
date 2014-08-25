#! /usr/bin/env python
# coding: utf-8

import  wx
import  wx.gizmos   as  gizmos

import  images


class TestPanel(wx.Panel):
    def __init__(self, parent ):
        wx.Panel.__init__(self, parent)

        self.treeCtrl = gizmos.TreeListCtrl(self, style=wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)

        isz = (16,16)  # image
        il = wx.ImageList(isz[0], isz[1])
        fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
        fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
        smileidx    = il.Add(images.Smiles.GetBitmap())

        self.treeCtrl.SetImageList(il)
        self.il = il

        # create some columns
        self.treeCtrl.AddColumn("Main column")
        self.treeCtrl.AddColumn("Column 1")
        self.treeCtrl.AddColumn("Column 2")
        self.treeCtrl.SetMainColumn(0) # the one with the tree in it...
        self.treeCtrl.SetColumnWidth(0, 175)


        self.root = self.treeCtrl.AddRoot("The Root Item")
        self.treeCtrl.SetItemText(self.root, "col 1 root", 1)
        self.treeCtrl.SetItemText(self.root, "col 2 root", 2)
        self.treeCtrl.SetItemImage(self.root, fldridx, which = wx.TreeItemIcon_Normal)
        self.treeCtrl.SetItemImage(self.root, fldropenidx, which = wx.TreeItemIcon_Expanded)


        for x in range(15):
            txt = "Item %d" % x
            child = self.treeCtrl.AppendItem(self.root, txt)  # tree part
            self.treeCtrl.SetItemText(child, txt + "(c1)", 1)  # description 1
            self.treeCtrl.SetItemText(child, txt + "(c2)", 2)  # description 2
            self.treeCtrl.SetItemImage(child, fldridx, which = wx.TreeItemIcon_Normal)
            self.treeCtrl.SetItemImage(child, fldropenidx, which = wx.TreeItemIcon_Expanded)

            for y in range(5):
                txt = "item %d-%s" % (x, chr(ord("a")+y))
                last = self.treeCtrl.AppendItem(child, txt)
                self.treeCtrl.SetItemText(last, txt + "(c1)", 1)
                self.treeCtrl.SetItemText(last, txt + "(c2)", 2)
                self.treeCtrl.SetItemImage(last, fldridx, which = wx.TreeItemIcon_Normal)
                self.treeCtrl.SetItemImage(last, fldropenidx, which = wx.TreeItemIcon_Expanded)


        self.treeCtrl.Expand(self.root)

class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None)
        self.tlc = TestPanel(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.tlc, 0, wx.EXPAND, 0)
        self.SetSizer(sizer)
        self.Layout()

        self.Show()

if __name__ == "__main__":
    app = wx.App()
    frame = Frame()
    app.MainLoop()

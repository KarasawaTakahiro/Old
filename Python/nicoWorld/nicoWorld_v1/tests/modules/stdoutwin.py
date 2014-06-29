
# coding: utf-8
"""
created on 2012/03/27
created by KarasawaTakahiro
"""

import wx

class StdoutWin(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.output_tc = wx.TextCtrl(self, style=wx.TE_MULTILINE
                                                |wx.TE_READONLY
                                                |wx.TE_AUTO_URL
                                                |wx.TE_BESTWRAP)

    def write(self, formar, text):
        """
        [oo] oooooo
        """
        self.output_tc.WriteText('[%s] %s\n' %(formar, text))

    def write_info(self, former, text):
        """
        ooo: ooo
        """
        if not self.IsShown(): self.Show()
        self.output_tc.WriteText('%s: %s\n' %(former, text))

    def write_simplicity(self, text):
        """
        oooooo
        """
        self.output_tc.WriteText(text)
        self.output_tc.WriteText('\n')


if __name__ == '__main__':
    
    class MainWin(wx.Frame):
        def __init__(self, *args, **kwargs):
            wx.Frame.__init__(self, *args, **kwargs)
            panel = wx.Panel(self)
            self.btn = wx.Button(panel, label='Push')
            
            self.stdout = StdoutWin(self, title='stdout/stderr')
            self.stdout.Hide()
            self.stdout_shown = False
            
            self.Bind(wx.EVT_BUTTON, self.OnButton, self.btn)
            
            self.timer = wx.PyTimer(self.write)
            self.timer.Start(1000)
            
        def OnButton(self, evt):
            if self.stdout_shown:
                self.stdout.Hide()
            else:
                self.stdout.Show()
            self.stdout_shown = not self.stdout_shown
    
        def write(self):
            self.stdout.write('formar', 'text')

    app = wx.App(redirect=False)
    win = MainWin(parent=None)
    win.Show()
    app.MainLoop()
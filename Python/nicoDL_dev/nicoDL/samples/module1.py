import  wx

class MyFrame(wx.Frame):
    """ based on Frame.py and Gauge.py """
    def __init__(
            self, parent, ID, title, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE
            ):
        wx.Frame.__init__(self, parent, ID, title, pos, size, style)
        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour('PINK')

        self.g1 = wx.Gauge(panel, -1, 50, (50, 50), (230, 25))
        self.Bind(wx.EVT_TIMER, self.TimerHandler)
        self.timer = wx.Timer(self)
        self.timer.Start(100)

    def TimerHandler(self, event):
        self.g1.Pulse()

class TestPanel(wx.Panel):
    """ based on Frame.py """
    def __init__(self, parent, log):
        self.log = log
        wx.Panel.__init__(self, parent, -1)

        b = wx.Button(self, -1, "RUN", (50,50))
        self.Bind(wx.EVT_BUTTON, self.OnButton, b)

    def OnButton(self, evt):
        win = MyFrame(self, -1, "Panel", size=(350, 200),
                      style = wx.DEFAULT_FRAME_STYLE)
        win.Show(True)

#-----------------------------------------------------------------
def runTest(frame, nb, log):
    win = TestPanel(nb, log)
    return win

#-----------------------------------------------------------------
if __name__ == '__main__':
    import sys,os
    import run
    run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])
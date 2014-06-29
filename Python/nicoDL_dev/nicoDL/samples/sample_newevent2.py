import sys
from StringIO import StringIO
from urllib2 import urlopen, HTTPError, URLError
import wx
from threading import Thread
from Queue import Queue

EVT_TYPE_GOTURL = wx.NewEventType()
EVT_GOTURL = wx.PyEventBinder(EVT_TYPE_GOTURL)

class GotURLEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid, value = None):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.value = value
    def GetValue(self):
        return self.value

class GetterThread(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.in_queue = Queue()
        self.parent = parent
        self.setDaemon(True)
        self.start()
    def request(self, url):
        self.in_queue.put(url)
    def run(self):
        retry = 3
        while retry > 0:
            try:
                url = self.in_queue.get()
            except:
                retry -= 1
                continue
            rc, hdr, body = get_url(url)
            if rc == 0:
                evt = GotURLEvent(EVT_TYPE_GOTURL, wx.ID_ANY, body)
                wx.PostEvent(self.parent, evt)

def get_url(url):
    try:
        fd = urlopen(url)
        rc = 0
        hdr = fd.info().dict
        segments = []
        while True:
            seg = fd.read()
            if seg == '':
                break
            segments.append(seg)
        body = ''.join(segments)
        fd.close()
    except HTTPError, val:
        hdr = val.info().dict
        rc = val.code
        body = None
        print 'HTTPError', rc
    except URLError, val:
        rc = -2
        hdr = None
        body = val
        print 'URLError'
    return rc, hdr, body

class imageFrame(wx.Frame):
    def __init__(self, parent, imglist):
        wx.Frame.__init__(self, parent, size = (300, 600), title = 'image viewer')
        self.Bind(EVT_GOTURL, self.OnGotURL)
        self.getter = GetterThread(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        for filename in imglist:
            self.getter.request(filename)
    def OnGotURL(self, event):
        imgdata = event.GetValue()
        stream = StringIO(imgdata)
        image = wx.ImageFromStream(stream)
        stream.close()
        bitmap = image.ConvertToBitmap()
        self.sizer.Add(wx.StaticBitmap(self, wx.ID_ANY, bitmap), 0, 0)
        self.Layout()
        self.Refresh()

app = wx.App(False)
frame = imageFrame(None, sys.argv[1:])
frame.Show()
app.MainLoop()
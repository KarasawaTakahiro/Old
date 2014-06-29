#!/usr/bin/env python
#coding: utf8

#userid="**********@***********"
#passwd="***********"
#smid="sm11977886"

import re, cgi, urllib, urllib2, cookielib, xml.dom.minidom
import datetime
import logging
import os.path

class nicovideoDL():
    def __init__(self, cdir):
        self.cdir = cdir
        self.date = datetime.datetime.today()

    def main(self, userid, passwd, smid, savedir, flag=True):
        """
        main(self, userid, passwd, smid, savedir, flag)
        flag == False でDLしない
        return
            videoTitle
        """


        #print 'UserID: %s' % userid
        #print 'PassWard: %s' % passwd
        #ログイン
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        """
        req = urllib2.Request("https://secure.nicovideo.jp/secure/login")
        req.add_data( urllib.urlencode( {"mail":userid, "password":passwd} ))
        res = opener.open(req)

        #タイトル取得(getthumbinfo)
        """
        data = urllib.urlopen("http://www.nicovideo.jp/api/getthumbinfo/"+smid).read()
        pTree = xml.dom.minidom.parseString(data)
        """
        for i in xrange(10):
            try:
                videoTitle = pTree.getElementsByTagName("title")[0].firstChild.data
                break
            except IndexError, mess:
                mess = str(mess)
                print 'nicovideoDL:', mess
                try:
                    videoTitle = str(smid)
                except StandardError:
                    break

        """
        # サムネ
        thumbnail = pTree.getElementsByTagName("thumbnail_url")[0].firstChild.data  # 動画時間
        print thumbnail

        #サムネのダウンロード
        res = opener.open(thumbnail)
        data = res.read()
        ext = res.info().getsubtype()

        ofh = open(os.path.join(savedir, "test_thumbnail"+"."+ext),"wb")
        if flag == True:
            ofh.write(data)
        return True


if __name__ == '__main__':
    a = nicovideoDL(os.getcwd())
    a.main("zeuth717@gmail.com","kusounkobaka","sm12323666",os.getcwd(),)

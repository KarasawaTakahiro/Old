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
        # logging setting
        logfile = ''.join([str(datetime.date.today()), '.txt'])
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(filename)s:%(lineno)d] %(asctime)s %(levelname)s %(message)s',
                            filename=''.join([self.cdir, '\log\\', logfile]), # logファイル置き場
                            filemode='a')

    def main(self, userid, passwd, smid, savedir, flag=True):
        """
        main(self, userid, passwd, smid, savedir, flag)
        flag == False でDLしない
        return
            videoTitle
        """
        for c in xrange(10):
            try:
                #print 'UserID: %s' % userid
                #print 'PassWard: %s' % passwd
                #ログイン
                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
                req = urllib2.Request("https://secure.nicovideo.jp/secure/login")
                req.add_data( urllib.urlencode( {"mail":userid, "password":passwd} ))
                res = opener.open(req)

                #タイトル取得(getthumbinfo)
                data = urllib.urlopen("http://www.nicovideo.jp/api/getthumbinfo/"+smid).read()
                pTree = xml.dom.minidom.parseString(data)
                for i in xrange(10):
                    try:
                        videoTitle = pTree.getElementsByTagName("title")[0].firstChild.data
                        break
                    except IndexError, mess:
                        mess = str(mess)
                        print 'nicovideoDL:', mess
                        logging.error(mess)
                        try:
                            videoTitle = str(smid)
                        except StandardError:
                            break

                # 説明取得
                try:
                    videoDescription = pTree.getElementsByTagName("description")[0].firstChild.data  # 動画説明
                except:
                    videoDescription = u''

                # 時間取得
                videoTime = pTree.getElementsByTagName("length")[0].firstChild.data  # 動画時間
                minute = int(videoTime.split(':')[0])
                second = int(videoTime.split(':')[1])

                #動画配信場所取得(getflv)
                res = opener.open("http://flapi.nicovideo.jp/api/getflv/"+smid).read()
                videoURL = cgi.parse_qs(res)["url"][0]
                print videoTitle
                print 'http://www.nicovideo.jp/watch/'+smid
                print u' => (%s) %s' % (str(smid),u'を開いています。')
                #logging.info(videoURL + u' => %s' % str(smid))

                # 終了時刻計算
                now = datetime.datetime.now()
                end = now + datetime.timedelta(minutes=minute, seconds=second)
                end = end.strftime('%m/%d %H:%M')
                print end, u'頃終了.'

                #動画のダウンロード
                opener.open("http://www.nicovideo.jp/watch/"+smid)
                mess = u''.join([videoTitle, '\n', u'(%s) を開いています。'%smid])
                #print mess
                logging.info(mess)
                res = opener.open(videoURL)
                data = res.read()
                ext = res.info().getsubtype()
                if re.search(r"low$",videoURL):
                    videoTitle = videoTitle + "(LOW)"

                if videoTitle.find('\\') == -1 and videoTitle.find('/') == -1:  # '\','/' の除外
                    pass
                else:
                    ed = []
                    a = list(videoTitle)
                    for i in a:
                        #print i, '->',
                        if i == u'\\' or i == u'/':
                            i = u'_'
                        #print i
                        ed.append(i)
                    videoTitle = ''.join(ed)

                #print videoTitle
                logging.info(unicode(videoTitle))
                ofh = open(os.path.join(savedir, videoTitle+"."+ext),"wb")
                if flag == True:
                    ofh.write(data)
                return (videoTitle, videoDescription)
                break

            except Exception, mess:
                print mess
                logging.error(mess)
                logging.error('retry')
            return False
            break
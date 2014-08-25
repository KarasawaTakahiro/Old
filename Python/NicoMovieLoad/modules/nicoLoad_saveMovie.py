#!/usr/bin/env python
# coding: utf-8

import cookielib
import urllib
import urllib2
import nicovideoAPI

class NicoLoad_SaveMovie():
    def __init__(self, bufferSize):
        self.flag_cancel = False
        self.bufferSize = bufferSize

    def save(self, movieId, nicoId, nicoPw, filename):
        """
        save method
        filename: abs file path (ext is none)
        """
        # 動画配信場所取得(getflv)
        api = nicovideoAPI.NicovideoAPI(movie_id=movieId)
        videoURL = api.get_storageURL(nicovideo_id=nicoId, nicovideo_pw=nicoPw)
        if videoURL.find("low") > -1:
            movieSize = api.get_movie_size_low()
        else:
            movieSize = api.get_movie_size_high()
        #ログイン
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        req = urllib2.Request("https://secure.nicovideo.jp/secure/login")
        req.add_data(urllib.urlencode({"mail":nicoId, "password":nicoPw}))
        res = opener.open(req)
        # 動画のダウンロード
        opener.open("http://www.nicovideo.jp/watch/"+movieId)
        res = opener.open(videoURL)
        ext = res.info().getsubtype()

        filename += "." + ext

        ofh = open(filename,"wb")
        while (int(ofh.tell()) < movieSize) and (not self.flag_cancel):
            print "%s/%s" % (ofh.tell(), movieSize)
            try:
                ofh.write(res.read(self.bufferSize))
            except:
                print "raise any error"
                break
        if ofh.closed == False:
            ofh.close()
        print ofh.closed
        self.flag_cancel = False
        return filename

    def cancel(self):
        """
        cancel loading
        """
        self.flag_cancel = True

if __name__ == "__main__":
    import os
    import os.path
    import threading
    import time
    saveMovie = NicoLoad_SaveMovie(1024)
    
    th = threading.Thread(target=saveMovie.save, args=("sm9932", "myremote717@gmail.com", "kusounkobaka", os.path.join(os.getenv("HOME"), "Desktop/sm9")))
    th.daemon = True
    th.start()

    time.sleep(10)
    print "cancel"
    saveMovie.cancel()



    th = threading.Thread(target=saveMovie.save, args=("sm9932", "myremote717@gmail.com", "kusounkobaka", os.path.join(os.getenv("HOME"), "Desktop/sm9")))
    th.daemon = True
    th.start()

    time.sleep(10)
    print "cancel"
    saveMovie.cancel()




#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging
import os.path

class YouTubeSearch():
    def __init__(self, debug):
        self.debug = debug
        self.fa = r'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\Temporary Files'
        self.fb = r'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\nicoDL'

        if self.debug:  # デバッグ時
            self.filename = 'test_YouTubeSearch.txt'  # ファイル名
            self.filemode = 'a'  # ファイルモード
            self.file = self.fb  # ファイル場所
            logfile = ''.join([str(datetime.date.today()), '-MylistSeach_test','.txt'])
        elif self.debug==False:
            self.filename = 'YouTubeSearch.txt'
            self.filemode = 'a'
            self.file = self.fa
            logfile = ''.join([str(datetime.date.today()), '-MylistSeach','.txt'])

        # logging setting
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(asctime)s]\n%(message)s\n',
                            filename=''.join([r'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\nicoDL\log', '\\', logfile]), # logファイル置き場
                            filemode='a')

    def main(self, video_id):
        u"""
        YouTubeのビデオIDを渡す.
        http://www.youtube.com/watch?v=*******
        """
        print '--- YouTubeSearch.main() ---------------' ##

        url = 'http://www.youtube.com/watch?v=%s' % str(video_id)
        f = open(os.path.join(self.file, self.filename), self.filemode)
        f.write(''.join([url, '\n']))
        print 'write: %s' % url
        f.close()

        print '--- /YouTubeSearch.main() --------------' ##

if __name__ == '__main__':
    search = YouTubeSearch(True)
    search.main('JHukDWrF9X8')

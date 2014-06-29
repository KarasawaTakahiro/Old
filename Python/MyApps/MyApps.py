#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import glob
import shutil

class MyApps():
    def __init__(self, waittime=3):
        self.cwd = os.getcwd()
        self.music = None
        self.waittime = waittime
        print u"""Hello!"""

    def main(self):
        self.func = raw_input('>>> ').lower()
        self.args = self.func.split()[1:]    # 引数
        # print self.args
        if self.func == 'end':
            # 終了
            self.end()
        elif self.func.startswith('music'):
            # MyApp_Music
            import modules.MyApps_Music as music
            self.music = music.Music(self.cwd, self.args)
            self.music.main()
            print self.music.re
                
        elif self.func.startswith('moviedl'):
            # MyApps_MovieDL
            try:
                self.moviedl = moviedl.MovieDL(self.cwd, self.args)
                self.moviedl.main()
            except NameError:
                import modules.MyApps_MovieDL as moviedl
                self.moviedl = moviedl.MovieDL(self.cwd, self.args)
                self.moviedl.main()
        elif self.func.startswith('timer'):
            # MyApps_Timer
            try:
                self.timer = timer.Timer(self.args)
                self.timer.main()
            except NameError:
                import modules.MyApps_Timer as timer
                self.timer = timer.Timer(self.args)
                self.timer.main()

        else:
            # 関数が見つからない
            print 'Tere is no "%s" function...' % self.func.split()[0]

    def end(self):
        print 'Can I quit?  -- y/n'
        self.ans = raw_input('>>>')
        if self.ans == 'y':# or 'Y' or 'Yes':
            sys.exit()
        else:
            pass

    def musicfile_copy(self):
        self.destinations = 'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\貴大\一時ファイル'
        self.musicfilename = 'modules\MyApps_Music_Files\*.m4a'
        self.path = os.path.join(os.getcwd(), self.musicfilename.encode('cp932'))
        for self.item in glob.glob(self.path):
            print self.item, '\n'
            shutil.copy(self.item, self.destinations.encode('cp932'))
        

if __name__ == '__main__':
    code = MyApps(10)
    try:
        while True:
            code.main()
    except SystemExit, error:
        import os.path, time
        print u'終了処理'
        # .m4a ファイルのコピー
        try:
            if code.music.re:
                print u'.m4a ファイルをコピーします。'
                code.musicfile_copy()
        except AttributeError, attributeerror:
            pass
        # .batファイルの削除
        p = os.path.join(code.cwd, 'modules')
        print u'ファイル検索'
        for dirpath, dirnames, filenames in os.walk(p, topdown=False):
            if not filenames == []:
                print u'\nbefore files'
                for i in filenames:    #ファイル名表示
                    i = ''.join(('-- ', i))
                    print i
                del i
        c = 0
        for filename in filenames:
            if os.path.splitext(filename)[1] == '.bat':
                os.remove(os.path.join(p, filename))
                c += 1
        for dirpath, dirnames, filenames in os.walk(p, topdown=False):
            if not filenames == []:
                print u'\nafter files'
                for i in filenames:
                    i = ''.join(('-- ', i))
                    print i
                del i
        print 'delete %i files' % c
                
        print ''.join((u'\n', unicode(code.waittime), u'秒後に閉じます。'))
        time.sleep(code.waittime)

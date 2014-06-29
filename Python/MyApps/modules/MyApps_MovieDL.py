# -*- coding:utf-8 -*-

import os
import os.path

class MovieDL():
    u"""動画ファイル保存\nGetter1使用"""
    def __init__(self, cdir, urls):
        self.urlist = urls
        # ディレクトリ設定
        self.cwd = os.path.join(cdir, 'modules')
        # Getter1 の場所
        self.getter1 = 'C:\Program Files\Getter1'
        # bat ファイル書き込み用
        self.bat = 'cd "%s"\n' % self.getter1

    def main(self):
        # DLリスト
        self.dlist = []
        for item in self.urlist:
            self.dlist.append(''.join(('"', item, '" ')))
            del item
        print u'ダウンロードリスト'
        for item in self.dlist:
            print item

        # バッチファイル作成
        self.batname = os.path.join(self.cwd, 'MyApp_MovieDL.bat')
        f = open(self.batname, 'w')
        f.write(self.bat.encode('cp932'))
        f.write('Getter1.exe ' )
        for item in self.dlist:
            f.write(item)
        f.write('\n')
        f.write('exit')
        f.close()

        # バッチファイル実行
        self.batf = os.path.join(self.cwd, self.batname)
        os.startfile(self.batf)
        print u'DLを開始します.'

if __name__ == '__main__':
    moviedl = MovieDL(['http://www.test/test.html'])
    moviedl.main()
        


# -*- coding: utf-8 -*-

import os
import os.path
import glob

class Music():
    u"""動画から音声を抜き出す\nEcoDecoTooL使用"""
    def __init__(self, cdir, args):
        # ディレクトリ設定
        self.path = os.path.join(cdir, 'modules')
        # EcoDecoTooL の場所
        self.ecodeco = 'C:\Program Files\EcoDecoTooL114'
        # batファイル書き込み用
        self.dos = 'cd %s\n' % self.ecodeco
        # 戻り値
        self.re = False
        # 取得拡張子
        self.extensions = ('flv', 'mp3')

    def main(self):
        self.folder = os.path.join(self.path, 'MyApps_Music_Files')  # 動画ファイルを置いておくフォルダ
        print u'ファイルを\n', self.folder, u'\nにおいてください。'
        if not os.path.exists(self.folder):  # 無ければ作成
            os.mkdir(self.folder)
        print u'おｋ？'
        self.ans = raw_input('--y/n>>>  ')
        if self.ans == 'y':
            pass
        else:
            print u'中止\n'
            return False
        
        # ファイルを取得
        print self.folder
        self.fname = []
        """for self.dire, self.dname, self.fname in os.walk(self.folder):
            del self.dire, self.dname
            if self.fname == []:
                print u'ファイルが見つかりません。\n'
                return False"""
        for a in self.extensions:
            for self.items in glob.glob(os.path.join(self.folder, ''.join(('*.', a)))):
                self.fname.append(self.items)
            
        self.files = []  # 変換ファイルリスト
        for item in self.fname:
            item = ''.join(('"', os.path.join(self.folder, item), '" '))
            self.files.append(item)
            del item
        print u'以下のファイルを変換します。'  # ファイル名表示
        for item in self.fname:
            print item
        print ''
            
        # バッチファイル作成
        self.batf = 'MyApp_Music.bat'
        f = open(os.path.join(self.path, self.batf), 'w')
        f.write(self.dos.encode('cp932'))
        f.write('EcoDecoTooL.exe ')
        for a in self.files:
            f.write(a)
        f.close()

        self.bat = os.path.join(self.path, self.batf)  # バッチファイル起動
        os.startfile(self.bat)

        print u'変換開始'
        self.re = True
        return self.re
    
if __name__ == '__main__':
    a = Music()
    a.main()

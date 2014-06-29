#!/usr/bin/env python
# coding: utf-8

import os
import os.path
import shutil
import subprocess
import sys

class nicoDL_EcoDeco():
    def __init__(self):
        # EcoDecoTool.exe パス
        self.ECODECOTOOL = r"C:\Program Files\EcoDecoTooL114\EcoDecoTool.exe"
        # 参照したいパス
        self.FOLDER = (r"C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\Temporary Files",
                       r"E:\Takahiro\niconico",
                       )
        # 検索単語 どれかが入っていれば実行
        self.WORDS = (u"初音ミク",
                      u"鏡音リン",
                      u"鏡音レン",
                      u"巡音ルカ",
                      u"GUMI",
                      u"今音ムイ",
                      u"作業用BGM",
                      )

    def main(self):
        """
        FOLDER に対してWORDSを検索しヒットしたらEcoDecoTool.exe 実行
        """
        if sys.platform == 'win32':
            pass
        else:  # windowsでなければreturn
            return False
        pathlist = []
        for item in self.FOLDER:
            # 参照先フォルダ決定
            if os.path.exists(item):
                pathlist.append(item)
        command = [self.ECODECOTOOL]
        print u'EcoDecoTool 適用リスト'
        flag = False
        for path in pathlist:
            for dirpath, dirnames, filenames in os.walk(path):
                if os.path.split(dirpath)[-1] == 'EcoDecoTooled':
                    continue
                for filename in filenames:
                    if self.filefilter(filename):
                        #print 'Append!! %s' % filename
                        print "", filename  # 表示用
                        command.append(os.path.join(dirpath, filename))
                        flag = True
        if flag:
            subprocess.call(command)  # えこでこ実行
        else:  # 該当ファイルなしで終了
            print u'該当ファイルなし'
            return True

        if os.path.exists(r"E:\Takahiro\niconico"):
            copypath = r"E:\Takahiro\niconico"
        elif os.path.exists(r"C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\Temporary Files"):
            copypath = r"C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\Temporary Files"
        else: return False;  # フォルダが見つからん
        copypath = os.path.join(copypath, 'EcoDecoTooled')
        if not os.path.exists(copypath): os.mkdir(copypath);  # フォルダなしで作成
        del command[0]  # えこでこのパスを除外
        for item in command:  # ファイル移動
            filename = os.path.split(item)[-1]
            shutil.move(item, os.path.join(copypath, filename)) #src:元 det:先


    def filefilter(self, filename):
        """
        .flv .mp4 を選別
        キーワードで選別
        """
        try:  # ファイル名をデコード
            filename = filename.decode('cp932')
        except:
            return False

        if filename.rfind('.mp4')>0 or filename.rfind('.flv')>0:
            # .mp4 .flv じゃなければ False
            pass
        else:
            #print filename
            return False

        for word in self.WORDS:
            #print filename
            try:
                if filename.find(word) >= 0:
                    #print True
                    return True
                else:
                    #print False
                    pass
            except:
                print u'Error %s' % filename
                return False
        else:
            return False

class MoveFile():
    """
    fromdir からtodirに.flv .mp4 ファイルを移動
    """
    def __init__(self):
        self.fromdir = r'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\Temporary Files'
        self.todir = 'E:\\Takahiro'

    def main(self):
        if os.path.exists(self.fromdir) == False: return False
        elif os.path.exists(self.todir) == False: return False
        else: pass
        print u"ファイル移動 \n%s\n  ->%s" % (self.fromdir,self.todir)

        movefiles = []
        sucsess = 0
        for dirpath, dirnames, filenames in os.walk(self.fromdir, False):
            for item in filenames:
                if item.rfind(".flv")>=0 or item.rfind(".mp4")>=0:
                    movefiles.append(item)
        for filename in movefiles:  # ファイル移動
            print filename,
            try:
                shutil.move(os.path.join(self.fromdir, filename), os.path.join(self.todir, filename)) #src:元 det:先
                print "...OK"
                sucsess += 1
            except:
                print

        print u" %i/%i ファイル成功" % (sucsess, len(movefiles))


if __name__ == '__main__':
    move=nicoDL_MoveFile()
    move.main()
    print u"end"


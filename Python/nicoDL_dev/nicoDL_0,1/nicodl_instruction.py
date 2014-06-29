#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os.path
import sys
import time


class nicoDL_Instruction():
    def __init__(self, cdir,debug=False):
        u"""
        self.instruction_txt      : ファイルのフルパス
        self.instruction_txt_name : ファイル名
        self.instruction_txt_dir  : ディレクトリ
        """
        self.debug = debug
        self.cdir = cdir
        self.instruction_txt_dir = self.cdir #r'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\nicoDL'
        self.flag_end = False

        if self.debug:  # debug 時
            self.instruction_txt_name = r'test-nicoDLInstruction.txt'
        elif self.debug == False:
            self.instruction_txt_name = r'nicoDLInstruction.txt'

        self.instruction_txt = os.path.join(self.instruction_txt_dir, self.instruction_txt_name)
        #print self.instruction_txt

        if not os.path.exists(self.instruction_txt):  # txtファイルが無ければ作成
            f = open(self.instruction_txt, 'w')
            f.close()

    def reset(self):
        u"""
        txtファイルをリセット
        """
        f = open(self.instruction_txt, 'w')
        f.close()

    def active(self):
        u"""
        ファイル作成
        """
        f = open(self.instruction_txt, 'w')
        f.close()

        if self.debug:
            front = 'test-'
        else:
            front = u''
        f = open('%sRe,Active!! %s.txt'%(front, time.strftime('%H-%M-%S')), 'w')
        f.write('Please del me.')
        f.close()

    def end(self):
        print u'10秒後に終了します.'
        self.reset()
        time.sleep(10)
        import winsound as ws
        ws.PlaySound('SystemExit', ws.SND_ALIAS)  # 音
        f = open(u'終了しました %s.txt'%time.strftime('%H-%M-%S'), 'w')
        f.close()
        self.flag_end = True  # 終了フラグ
        sys.exit()

    def main(self):
        f = open(self.instruction_txt, 'r')
        instruction = f.readline().strip('\n').lower()

        # 関数定義
        if instruction == 'quit':
            self.end()
        elif instruction == 'active':
            self.active()

        self.reset()
        f.close()


if __name__ == "__main__":
    instruction = nicoDL_Instruction(debug=True)
    c = 0
    while True:
        c += 1
        print c

        instruction.main()
        time.sleep(0.1)
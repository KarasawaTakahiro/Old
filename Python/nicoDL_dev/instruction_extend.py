#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading

class Instruction_Extend(threading.Thread):
    def __init__(self, n, debug=True):
        u"""
        n にbool値を渡す
        Testをインポートした側からself.INSTRUCTIONを参照すればいい
        """
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.INSTRUCTION = n

        if debug:
            self.file = 'test_INSTRUCTION.txt'
        else:
            self.file = 'INSTRUCTION.txt'

        f = open(self.file, 'w')
        f.close()


    def run(self):
        while True:
            u"""
            self.INSTRUCTION の bool値を変える
            """
            f = open(self.file, 'r')

            if f.readline().strip('\n') == 'True':
                self.INSTRUCTION = True
            else:
                self.INSTRUCTION = False

            f.close()
            time.sleep(0.1)
        print 'Instruction_Extend() is end.'
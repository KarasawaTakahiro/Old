#! /usr/bin/python
# coding: utf-8

import os
import os.path
import sys

class NicoMovieLoad():
    def __init__(self):
        self.movies = sys.argv[1:]

    def main(self):
        """
        やるべきこと

        コマンド待機 => self
        取得動画ID取得 => self コマンド
        保存 => 保存機構はバックで動作させる
        マイリス更新確認 => バックで起動
        """
        """
        コマンド
         文字列を受け取る
         スペースで区切る
         0番目はコマンド
         1-n番目はオプション
         オプションと引数を識別する
         オプション -xxx
         引数 yyy
         プロトコル: [command, {options}]
         オプション: {-xxx:yyy, }
        """
        RUNNING = True
        while(RUNNING):
            line = u""
            line = raw_input(u">>> ")

    def load(self):


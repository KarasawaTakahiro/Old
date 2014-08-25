# 
# coding: utf-8

import os
import re
import threading
import time
from modules.nicoLoad_database import Database
from modules.nicoLoad_exceptions import *
from modules.nicoLoad_various import nicoLoad_Various as Various
from modules.nicoLoad_queue import nicoLoad_queue as Queue
from modules.nicovideoAPI import NicovideoAPI

"""
動画保存用ループ実行（キューから順に動画IDを取ってきて保存するもの
 呼ばれたときに無限ループしておく
 終了時にやめる

保存キューへの追加タイミング
 loadコマンドがmovieId付きで呼ばれたとき
 loadコマンドが引数なしで呼ばれたとき(全保存)

"""

"""
DLするときにやること
-動画IDを取得 > 動画ID
-DBに保存 > bool
-キューに追加 > bool
--キューのチェック > bool 待ちがあるかどうか
--待ちの動画IDを取得 > 動画ID
--動画名を取得 > str
--動画を保存 > bool 中断の方法を考える
--コメントの取得、保存
--DBに保存
--サムネの取得、保存
--DBに保存

RSS
-チェックするマイリストを決める
-マイリスト内の動画一覧を取得
-動画に対して取得済みか確認
-未取得のものはキューに追加

"""

class NicoLoad_Load():
    def __init__(self, log, status, ):#databaseObj):
        """
        log: modules.nicoLoad_base.Log()
        """
        self.log = log
        self.status = status
        self.db = Database()#databaseObj

        if not(self.db.extMovieTable() and self.db.extMylistTable() and self.db.extMylistHasMovieTable()):
            self.db.ctTable()
        self.queue = Queue()

        self.__loading = False  # 動画を保存しているか is storing movie or not
        self.waitTime = 1

         # self.movieLoadLoop()  # 保存用の無限ループ
        movieLoadThread = threading.Thread(target=self.movieLoadLoop)
        movieLoadThread.daemon = True
        movieLoadThread.start()

    def movieLoadLoop(self):
        """
        保存用ループ
        loop for strage
        """
        # 既に動いていたら  if already running
        while True:
            try:
                movieid = self.movieQueueGet()
                self.status.setLoadingMovieid(movieid)
                self.movieLoad()
            except QueueEmptyError:
                self.status.setLoadingMovieid(u"waiting")
                time.sleep(self.waitTime)

    # まとめ系
    def nicoLoad_Load(self, *args):
        """
        load全般まとめ関数
        General Summary of load function
        コマンドから実行する関数を振り分ける
        Distributes the function to be executed from the command
        """
        option = args[1]
        if option.has_key(args[0]):
            # 引数付き
            url = option[args[0]]
            self.movieLoad(url)
        else:
            # 引数なし
            self.movieLoadAll()

    def rss(self, *args):
        """
        rss
         -id mylistid_1, mylistid_2, ...
        """
        option = args[1]
        del option[args[0]]
        if len(args) == 0:
            self.rssAll()
        else:
            for mylistid in option["-id"]:
                self.rssOne(mylistid)

    def movieLoadAll(self):
        """
        すべての動画を保存
        save all videos
        """
        for movieid in self.db.getMovieState0():
            self.movieQueueAdd(movieid)

    def regNicoInfo(self, *args):
        """
        ニコニコID,PW保存
        save niconico ID & PW
        """
        print u"ニコニコ動画のIDを入力してください"
        nicoid = raw_input(">>> ")
        print u"ニコニコ動画のPWを入力してください"
        nicopw = raw_input(">>> ")
        self.db.svNicoid(nicoid)
        self.db.svNicopw(nicopw)
        return True
    def regGmailInfo(self, *args):
        """
        GmailID,PWを保存
        save Gmail ID & PW
        """
        gmailid = raw_input(u"GmailのIDを入力してください\n>>> ")
        gmailpw = raw_input(u"GmailのPWを入力してください\n>>> ")
        self.db.svGmailid(gmailid)
        self.db.svGmailpw(gmailpw)
    def regSavedir(self, *args):
        """
        保存フォルダを保存
        save the folder for saving
        """
        flag = False
        while True:
            savedir = raw_input(u"保存フォルダを入力してください\n>>> ")
            flag = os.path.exists(os.path.abspath(savedir))
            if flag:
                break
            else:
                print u"入力されたフォルダは存在しません"

        self.db.svSavedir(savedir)
        return True

    def getNicoInfo(self):
        """return (nicoid, nicopw)"""
        return (self.db.getNicoid(), self.db.getNicopw())
    def getGmailInfo(self):
        """return (gmailid, gmailpw)"""
        return (self.db.getGmailid(), self.db.getGmailpw())
    def getSavedir(self):
        """return savedir"""
        return self.db.getSavedir()

    def movieQueueAdd(self, movieid):
        """
        保存キューに追加
        add to the queue for string
        """
        print "addQueue: %s" % movieid
        self.queue.add(movieid)
    def movieQueueAddFront(self, movieid):
        """
        保存キューの先頭に追加
        added to the top of the queue for string
        """
        print "addQueue: %s" % movieid
        self.queue.addFromnt(movieid)
    def movieQueueaddNext(self, movieid):
        """
        保存キューの次に追加
        added to the queue for string the second
        """
        print "addQueue: %s" % movieid
        self.queue.addNext(movieid)
    def movieQueueGet(self):
        """
        キューから取得
        retrived from the queue
        """
        return self.queue.get()
    def movieLoadDone(self):
        """
        タスクの終了を伝える 
        convey the completetion of the task
        タスクを実行したら呼び出す
        call to perform the task
        
        """
        self.queue.done()
        self.__loading = False
        self.status.chLoadingMovie()

    def movieLoad(self, movieid):
        """
        動画を保存
        save videos
        """
        if self.db.extMovieidInTable(movieid):
            # already resists
            self.db.setMovieState(movieid, 0)
        else:
            self.db.addMovie(movieid)  # resists for database
        api = NicovideoAPI(movie_id=movieid)
        title = api.get_movie_title()
        # ext = api.get_movie_type()
        nicoid = self.db.getNicoid()
        nicopw = self.db.getNicopw()
        savedir = getSavedir()
        self.__loading = True
        self.status.chLoadingMovie(self.__loading)
        self.db.setMovieTitle(movieid, title)
        self.db.setMovieDescription(movieid, api.get_movie_description())
        self.db.setMovieLength(movieid, api.get_movie_length())
        self.status.setLoadingMovieid(movieid)
        moviePath = api.save_movie(nicoid, nicopw, savedir)
        self.db.setMoviePath(movieid, moviePath)
        self.db.setMovieThumbnail(movieid, api.save_thumbnail(savedir))
        self.db.setMovieComment(movieid, api.save_comment(nicoid, nicopw, savedir, title))
        self.db.setMovieState(movieid, 1)
        self.movieLoadDone()
        return True

    def rssOne(self, mylistid):
        """
        マイリスRSS
        RSS for mylist
        """
        various = Various(self.db)
        for movieid in  various.rsscheck(mylistid):
            self.movieQueueAdd(movieid)

    def rssAll(self):
        """
        マイリスRSS
        RSS for mylist
        """
        various = Various(self.db)
        for mylistid in self.db.getMylistAll():
            for movieid in various.rsscheck(mylistid):
                self.movieQueueAdd(movieid)

    def setWaitTime(self, minute):
        """
        chenge wait time when load queue is empty
        """
        self.WaitTime = minute

    def exit(self):
        """
        Exit
        """
        pass


if __name__ == "__main__":
    pass


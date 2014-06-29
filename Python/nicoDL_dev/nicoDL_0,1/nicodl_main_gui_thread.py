# -*- coding: utf-8 -*-

import datetime
import free_disc_space as freespace
import logging
import nicodl_instruction as Instruction
import niconicoDL as nicoDL
import niconico_mylist_control as Mylist_Control
import niconico_mylist_search as Mylist_Search
import nicodl_sendmail as SendMail
import re
import os.path
import pickle
import sys
import threading
import time
import youtube_search as youtube_search

from imaplib import *

u"""
code ### : 表示用
code ##  : 必要空白行
"""


class RemoteNicovideoDL(threading.Thread):
    def __init__(self, directory, userid, passwd, savedirectory, basesavedirectory, flag=True, debug=True):
        """
        debug = True/False
        """
        # threading
        threading.Thread.__init__(self)
        self.setDaemon(True)

        self.cdir = os.getcwd()  # カレントディレクトリ
        self.front =  r'http://www.nicovideo.jp/watch/'
        self.ffront = r'http://www.nicovideo.jp/' #不要？
        self.directory = directory
        self.userid = userid  # ニコニコ
        self.passwd = passwd  # ニコニコ
        try:
            f = open('info.ndl')
        except IOError:
            print u'nicodl_setup.exe を起動して、初期設定を行なってください。'
            sys.exit()
        info = pickle.load(f)
        self.gid = info['GMAIL_ID']  # gmail
        self.gpw = info['GMAIL_PW']  # gmail
        self.toadd = info['TO_ADDR']  # メール送信先
        self.savedirectory = savedirectory
        self.basesavedirectory = basesavedirectory
        self.flag = flag
        self.debug = debug
        self.empty = True  # emptyメッセージ表示フラグ
        self.message = u'NicoVideoDL'  # GUI表示用
        self.flag_end = False

        if debug:
            self.start_wait_time = 1  # windows 起動待ち
            self.timeout_wait_time = 3  # Internet 接続失敗時
            self.wait_time = 1  # DL間隔
            self.empty_wait_time = 3  # DLリストが空の時の待ち時間
            self.backupfile = 'test2_backup.txt'
            logfile = ''.join([str(datetime.date.today()), ' test.txt'])
        else:
            self.start_wait_time = 3#00  # 5分
            self.timeout_wait_time = 300  # 5分
            self.wait_time = 300
            self.empty_wait_time = 600
            self.backupfile = 'backup.txt'
            logfile = ''.join([str(datetime.date.today()), '.txt'])

        # logging setting
        if False == os.path.exists('.\\log'):
            os.mkdir('.\\log')
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(filename)s:%(lineno)d] %(asctime)s %(levelname)s %(message)s',
                            filename=''.join([self.cdir, '\log\\', logfile]), # logファイル置き場
                            filemode='a')

    def find(self, text):
        u"""
        text から動画URLを返す
        text からマイリスが見つかった場合は Mylist_Search.MylistSearch.main() を使用
        text からYouTube動画URLが見つかった場合はYouTubeSearch.YouTubeSearch.main() を使用

        return -1 はメール削除後continue

        return
          動画URL: (URL, bool)
          mylist : -1
          YouTube: -1

          other  : False
        """
        #print '--- find() -----------------------------'
        matched = re.search('[sn][mo]\d+', text)  # videoID検索
        #print 'find() matched videoID: %s' % matched ###
        if matched:
            video_id = matched.group()
            print 'Hit!: %s' % video_id ###
            url = ''.join([self.front, video_id])
            #print '--- /find() ----------------------------'
            print ##
            return (url, True)  # (URL, bool)

        matched = re.search('mylist/\d+', text)  # mylistID検索
        #print 'find() matched mylistID: %s' % matched ###
        if matched:
            mylist_id = matched.group().strip('mylist/')
            print 'Hit! mylistID: %s' % mylist_id ###
            u"""mylist_control"""
            control = Mylist_Control.MylistControl(self.directory, mylist_id, self.debug)
            control.writing_function_group()
            u"""mylist_control end"""
            #mylistsearch = Mylist_Search.MylistSearch(self.debug)
            #mylistsearch.main(mylist_id)
            print 'Waiting...'
            time.sleep(5)
            #print '--- /find() ----------------------------'
            print ##
            return -1

        matched = re.search('v=\w+', text)  # YouTube検索 #youtube.com/watch?
        #print 'find() matched youtube_videoID: %s' % matched
        if matched:
            youtube_video_id = matched.group().strip('v=')
            print 'Hit! mylistID: %s' % youtube_video_id ###
            youtubesearch = youtube_search.YouTubeSearch(self.debug)
            youtubesearch.main(youtube_video_id)
            #print '--- /find() ----------------------------'
            print
            return -1

        #print '--- /find() ----------------------------'
        print ##
        return False

    def geturl(self):
        u"""
        GmailにアクセスしメールからURL取得
        動画IDをリストで返す
        """
        urllist = []
        c = 0
        mess = u'Gmail にアクセスしています.'
        self.message = mess
        print mess
        print ##
        while True:
            try:
                imap = IMAP4_SSL('imap.gmail.com')
                break
            except BaseException, mess:
                logging.error(mess)
                if c > 10:
                    import sys
                    logging.error('gmail cant be conected...')
                    sys.exit()
                elif c <= 10:
                    time.sleep(600)
                c += 1

        imap.login(self.gid, self.gpw)  # Gmail login
        imap.select()

        backupf = open(self.backupfile, 'a')

        _,[data] = imap.search(None,'ALL')
        for i in data.split(' '):
            try:
                _,sub = imap.fetch(i, '(RFC822.TEXT)')
            except:
                return False
            text = sub[0][1].strip()  # メール本文すべて
            #print text ###
            url = self.find(text)  # find()でURL検索 #####
            #print url ###
            if url == False:  # niconicoアドレス見つからない
                continue
            elif url == -1:
                if not self.debug:
                    imap.store(i, '+FLAGS', '\Deleted')  # 動画ID以外のときメール削除
                continue
            backupf.write(''.join([u'', u';',url[0], '\n']))  # バックアップ
            urllist.append(url[0])
            if not self.debug:
                if url[-1]:
                    imap.store(i, '+FLAGS', '\Deleted')  # メール削除
        imap.logout()
        backupf.close()


        #print u'DLファイルリスト'
        #print urllist
        chengedurllist = [] # 動画IDのみに変換
        for a in urllist:
            url = a.strip(r'a, o, c, e, d, i, h, j, \/, ., p, n, t, w, v, :,')
            chengedurllist.append(url)
            #print url
            break

        #print 'chengedurllist:',chengedurllist
        return chengedurllist

    def sorting(self):
        u"""
        バックアップファイルのダブり解消
        """
        befors = []  # もともとのやつ
        afters = []  # 書き込み決定
        after = []  # return 用
        try:
            f = open(self.backupfile, 'r')
        except IOError:
            return []
        items = f.readlines()
        f.close()
        for i in items:
            i =  i.split(';')
            i = [i[0], i[1].strip('\n')]
            #print 'i:',i
            befors.append(i)
        #print 'befors:',befors
        print

        for b in befors:  # 加えたい
            b_append = True
            #print '*******************************'
            #print 'b:', b[1]
            for a in afters:  # 入ってる
                #print 'a:', a[1]
                if  b[1] == a[1]:  # かぶったらFalse
                    b_append = False
                    break

            if b_append:  # Trueのままならappend()
                afters.append(b)
                #print '!append!'
        for i in afters:
            after.append(';'.join(i))

        f = open(self.backupfile, 'w')
        for i in after:
            f.write(i)
            f.write('\n')
        f.close()


    def backupstrdel(self, string):
        string = string.strip('\n')  # 除外文字列
        strlist = []  # 色々

        r = open(self.backupfile, 'r')
        for a in r.readlines():
            #print a
            a = a.split(';')
            strlist.append([a[0],a[1].strip('\n')]) # strlist == [[func, URL], [func, URL]]
            #print a.strip('\n') ###
        r.close()
        #print strlist
        #print

        for b in strlist:  # 除外
            if b[1] == string:
                removedstring = b
                #print 'Hit: %s' % b  ###
                strlist.remove(removedstring)
        #print strlist
        w = open(self.backupfile, 'w')  # 書き込み
        for i in strlist:
            i = ';'.join(i)
            w.write(''.join([i,'\n']))
            #print i
        w.close()

    def run(self):#, userid, passwd, savedirectory, basesavedirectory, flag=True):
        u"""
        flag: DLするか
        """

        time.sleep(self.start_wait_time)
        if self.debug:
            print 'Start!!'
        logging.info('   nicoDL is starting!!')
        self.sorting()

        sendmail = SendMail.nicodl_sendmail(self.gid, self.gpw, self.toadd, self.cdir)  # 完了メール送信用
        nicodl = nicoDL.nicovideoDL(self.cdir)
        instruction = Instruction.nicoDL_Instruction(self.cdir)  # 命令

        if self.debug:  # 保存場所
            self.savedirectory = r'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\nicoDL'

        message = u''  # メール本文

        """start while loop """
        while True:
            movies = []

            for i in self.geturl():  # Gmailチェック
                movies.append({'func':'', 'id':i[0]})

            instruction.main()


            control = Mylist_Control.MylistControl(self.directory, debug=self.debug)
            self.message = u'更新チェック'
            control.rss()  # 更新チェック
            self.message = u'BUFに書き込み中'
            control.backup_write()  # 未DLをバックアップファイルに書き込み
            del control

            self.sorting()

            f = open(self.backupfile, 'r')  # バックアップファイルから読み込み
            for i in f:
                items = i.split(';')
                movid = items[1].strip('a, o, c, e, d, i, h, j, /, ., p, n, t, w, v, :, \n')  # videoID
                #print 'movid:',movid
                movies.append({'func':items[0], 'id':movid})
            f.close()

            # ダウンロードリスト表示　　
            if not movies == []:  # ダウンロードリスト表示
                n = len(movies)
                mess = 'Download List (%i)' % n
                print mess
                logging.info(mess)
                if self.debug:
                    for i in movies:
                        print i['id'].strip('\n\r')
                        #logging.info(i.strip('\n\r'))
                self.empty = True
            else:
                if self.empty:
                    mess = 'Empty.'
                    self.message = mess
                    print mess
                    logging.info(mess)
                    self.empty = False
                    instruction.main()
                    time.sleep(self.empty_wait_time)
                else:
                    pass

            timeout = 0  # timeout counter
            for movie_dic in movies:
                instruction.main()
                # ドライブの容量確認
                if os.path.exists(self.savedirectory) and freespace.free_disk_space(self.savedirectory)[0] > 1:  # 保存場所決定
                    pass
                else:
                    if os.path.exists(self.basesavedirectory):
                        if freespace.free_disk_space(self.basesavedirectory)[0] > 1:
                            self.savedirectory = self.basesavedirectory
                        else:
                            mess = u'%sが見つからず\n%sの容量がありません.' % (self.savedirectory, self.basesavedirectory)
                            print mess
                            f = open(os.path.join(self.cdir, r'log\Error.txt'), 'a')
                            f.write(''.join(('[%s] '% time.strftime('%Y/%m/%d %H:%M:%S'), mess, '\n')))
                            f.close()
                            self.message = mess
                            time.sleep(300)
                            continue
                    else:
                        mess = u'ディレクトリが見つかりません.'
                        print mess
                        f = open(os.path.join(self.cdir, r'log\Error.txt'), 'a')
                        f.write(''.join(('[%s] '% time.strftime('%Y/%m/%d %H:%M:%S'), mess, '\n')))
                        f.close()
                        self.message = mess
                        time.sleep(300)
                        continue
                # ここまで

                mess = '****************************************'
                print mess
                logging.info(mess)
                #print 'dic   :',movie_dic
                #print 'dic_id:',movie_dic['id']
                """flags"""
                flag_mylist = False  # マイリス管理用フラグ
                """"""
                """
                flag judge
                """
                #print 'func:',movie_dic['func']
                if movie_dic['func'].rfind(u'#') == 0:  # #* だったら
                    flag_mylist = True
                """
                /flag judge
                """

                self.message = u'DL中\nhttp://www.nicovideo.jp/watch/'+movie_dic['id']

                DL = nicodl.main(self.userid, self.passwd, movie_dic['id'], self.savedirectory, self.flag)
                #print 'DL:',DL
                if DL == False:  # timeout
                    self.message = u'インターネット接続に失敗...'
                    timeout += 1
                    if timeout == 10:  # timeout
                        import sys
                        mess = "Timeout, don't conect the Internet."
                        print mess
                        logging.error(mess)
                        sys.exit()
                    time.sleep(self.timeout_wait_time)
                    continue
                timeout = 0

                mess ='Download End.'
                print mess
                logging.info(mess)
                print

                if self.debug == False:
                    sendmail.main(''.join([DL[0], message, '\n\n', DL[1]]), ''.join([movie_dic['id'], message]))  # 完了メール送信
                if self.debug == False:
                    if not DL == False:
                        self.backupstrdel(''.join([self.front, movie_dic['id']])) # backup.txtから削除

                if flag_mylist:
                    u"""
                    データベース書き換え
                    動画IDと#*を渡して、Tにする関数
                    """
                    control = Mylist_Control.MylistControl(self.directory)
                    self.message = u'DB書き換え中...'
                    control.reflag(movie_dic['id'], movie_dic['func'])
                    flag_mylist = False

                mess = '****************************************'
                print mess
                logging.info(mess)
                instruction.main()
                mess = 'Waiting...'
                self.message = mess
                print mess
                time.sleep(self.wait_time)
                mess = 'Next...'
                self.message = mess
                print mess
                logging.info(mess)



            if self.debug:
                print 'Finish!! -1'
                break
                #sys.exit()

        """end loop"""

        print 'Finish!!'

if __name__ == '__main__':

    #ユーザー設定部
    directory = ur'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\nicoDL'
    user_id = 'zeuth717@gmail.com'  # ニコニコアカウント
    pass_wd = 'kusounkobaka'  # ニコニコパス
    base_save_dir = r'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\Temporary Files'
    save_dir = r'E:\Takahiro\movie'

    nicodl = RemoteNicovideoDL(directory, user_id, pass_wd, save_dir, base_save_dir, debug=False) # debug = bool
    nicodl.start()


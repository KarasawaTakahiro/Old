# coding: utf-8

import cliantinfoformat as CliantInfo
import nicodl_various as Various
import os
import pickle
import re
import sys
import time

from imaplib import *

class nicoDL_DL():
    def __init__(self, infofiledir):
        """
        gmailID
        gmailPW
        nicoID
        nicoPW
        to_address
        savedirectory
        """
        self.infofilepath = os.path.join(infofiledir, 'info.ndl')

        self.gmail_id = self.pickup('gmail_id') 
        self.gmail_pw = self.pickup('gmail_pw')
        self.nico_id = self.pickup('nico_id')
        self.nico_pw = self.pickup('nico_pw')
        self.toaddr = self.pickup('toaddr')
        self.savedir = self.pickup('savedir')
        self.cdir = os.getcwd()

    def find(self, text):
        u"""
        textからmyformatを返す
        textからマイリスが見つかった時はMylist_Search.MylistSearch.main()

        return
                       動画URL: movie format
          mylist : mylist format
          YouTube:

          other  : False
        """
        nicodl_various = Various.nicoDL_Various()
        #print '--- find() -----------------------------'
        #print text
        matched = re.search('[s][mo]\d+', text)  # videoID検索
        #print 'find() matched videoID: %s' % matched ###
        if matched:
            video_id = matched.group()
            print 'Hit!: %s' % video_id ###
            myformat = nicodl_various.make_myformat(movie_id=video_id, state=False, form='MOVIE')  # movie format
            #print '--- /find() ----------------------------'
            #print ##
            print self, 'myformat:', myformat
            return myformat

        matched = re.search('mylist/\d+', text)  # mylistID検索
        #print 'find() matched mylistID: %s' % matched ###
        if matched:
            mylist_id = matched.group().strip('mylist/')
            print 'Hit! mylistID: %s' % mylist_id ###
            myformat = nicodl_various.make_myformat(mylist_id=mylist_id, form='MYLIST')  # mylist format
            #print 'Waiting...'
            time.sleep(0.1)
            #print '--- /find() ----------------------------'
            #print ##
            return myformat

        #print '--- /find() ----------------------------'
        #print ##
        return False

    def geturl(self):
        u"""
        Gmailにアクセスしメールから本文取得
        """

        #print ##

        #print "Gmail ID:",self.gmail_id
        #print "Gmail PW:",self.gmail_pw

        imap = IMAP4_SSL('imap.gmail.com')
        imap.login(self.gmail_id, self.gmail_pw)  # Gmail login
        imap.select()

        _, [data] = imap.search(None, 'ALL')
        for i in data.split(' '):
            _, sub = imap.fetch(i, '(RFC822.TEXT)')
            text = sub[0][1].strip()  # メール本文すべて
            myformat = self.find(text)
            #if (self.debug == False) and (myformat != False):  # 見つかって非デバック時
            if myformat != False:
                imap.store(i, '+FLAGS', '\Deleted')  # メール削除
                imap.logout()
                return myformat
            #elif (self.debug == True) and (myformat != False):  # 見つかってデバック時
                #imap.logout()
                #return myformat
            else: continue

        imap.logout()
        return False

    def mkcliantinfoformat(self, gmail_id, gmail_pw, nico_id, nico_pw, toaddr, savedir):
        if savedir=='':  savedir = '.'
        return CliantInfo.CliantInfoFormat(gmail_id, gmail_pw, nico_id, nico_pw, toaddr, savedir)

    def pickup(self, choice):
        # 想定外の引数
        if not choice in ['gmail_id', 'gmail_pw', 'nico_id', 'nico_pw', 'toaddr', 'savedir']:
            raise ValueError, u'%sはありません'%str(choice)
        info = self.infofileopen()
        return getattr(info, choice)

    def rewrite(self, choice, value):
        info = self.infofileopen()
        info[choice] = value
        self.infofilesave(info)
        return

    def infofileopen(self):
        """
        return info_obj
        """
        # infoファイルが見つからない
        if not os.path.exists(self.infofilepath):
            # 新規作成
            print u'infoファイルが見つかりませんでした。\n新規作成します。'
            self.infofilesave(self.mkcliantinfoformat("","","","","",""))
        ff = open(self.infofilepath)
        info = pickle.load(ff)
        ff.close()
        return info
    
    def infofilesave(self, info_obj):
        ff = open(self.infofilepath, 'w')
        pickle.dump(info_obj, ff)
        ff.close()
        
        
if __name__ == '__main__':
    nico = nicoDL_DL(os.getcwd())
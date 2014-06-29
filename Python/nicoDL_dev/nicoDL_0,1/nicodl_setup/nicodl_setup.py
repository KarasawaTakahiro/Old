#!/usr/bin/env python
#-*- coding: utf-8 -*-

import getpass
import pickle

def main():
    flag = False
    while flag == False:
        info ={}  # 情報
        print u'初期設定を開始します。'
        print
        print u'ニコニコ動画のIDを入力してください。'
        niconico_user_id = raw_input('>>> ')
        print u'ニコニコ動画のPWを入力してください。'
        niconico_pass_wd = raw_input('>>> ')
        print u'GmailのIDを入力してください。'
        gmail_id = raw_input('>>> ')
        print u'GmailのPWを入力してください。'
        gmail_pw = raw_input('>>> ')
        print u'完了通知メールのあて先を入力してください。'
        to_addr = raw_input('>>> ')
        print u'動画を保存するフォルダを","で区切って2つ入力してください。\n（2つ目以降は予備フォルダ）'
        dire = raw_input('>>> ')
        save_dir = dire.split(',')

        info ={'NICO_ID':niconico_user_id,
               'NICO_PW':niconico_pass_wd,
               'GMAIL_ID':gmail_id,
               'GMAIL_PW':gmail_pw,
               'TO_ADDR':to_addr,
               'SAVE_DIR':save_dir,
               }

        # pickle化
        f = open('info.ndl', 'w')
        pickle.dump(info, f)
        f.close()

        print u'確認してください。\n'
        print u'ニコニコ動画ID\n %s' % info['NICO_ID']
        print u'ニコニコ動画PW\n %s' % info['NICO_PW']
        print u'Gmail ID\n %s' % info['GMAIL_ID']
        print u'Gmail PW\n %s' % info['GMAIL_PW']
        print u'メールあて先\n %s' % info['TO_ADDR']
        print u'保存フォルダ'
        for i in info['SAVE_DIR']:
            print u'', i

        print u'間違いはありませんか？ '
        diff = raw_input('Yes/No\n>>> ')
        if diff == u'Yes' or diff == u'yes' or diff == u'y':
            flag = True
        else:
            flag = False

    print
    print u'Enter で終了.'
    raw_input('')

if __name__ == '__main__':
    main()

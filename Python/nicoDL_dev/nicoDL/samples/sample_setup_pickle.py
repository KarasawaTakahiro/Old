#!/usr/bin/env python
#-*- coding: utf-8 -*-

import getpass
import pickle

info ={}  # 情報

niconico_user_id = raw_input(u'ニコニコ動画のIDを入力してください。\n>>>')
print u'ニコニコ動画のPWを入力してください。'
niconico_pass_wd = getpass.getpass('>>>')
gmail_id = raw_input(u'GmailのIDを入力してください。\n>>>')
print u'GmailのPWを入力してください。'
gmail_pw = getpass.getpass('>>>')
dire = raw_input(u'動画を保存するフォルダを入力してください。\n","で区切って2つまで入力できます。\n（2つ目以降は予備フォルダ）\n>>>')
save_dir = dire.split(',')

info ={'NICO_ID':niconico_user_id,
       'NICO_PW':niconico_pass_wd,
       'GMAIL_ID':gmail_id,
       'GMAIL_PW':gmail_pw,
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
print u'保存フォルダ'
for i in info['SAVE_DIR']:
    print u' ' + i
print
print u'Enter で終了.'
print u'間違いがあれば再入力してください。'
raw_input('')

"""
user_id = 'zeuth717@gmail.com'  # ニコニコアカウント
pass_wd = 'kusounkobaka'  # ニコニコパス
base_save_dir = r'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\Temporary Files'
save_dir = r'E:\Takahiro\movie'
"""


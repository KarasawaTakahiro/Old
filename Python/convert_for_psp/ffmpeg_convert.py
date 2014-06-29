
#coding: utf-8

# 2012/02/25 更新

import os
import os.path
import subprocess
import sys,time

import sendgmail as gmail

class FFMpeg_convert():
    def __init__(self, filename):
        self.filename = os.path.abspath(filename)  # 変換ファイル名
        self.ffmpeg = os.path.join(os.getcwd(), 'ffmpeg.exe')  # ffmpegの場所


    def main(self):
        frontname = os.path.basename(self.filename).split('.')[0]  # ファイル名特定
        filedir = os.path.dirname(self.filename)
        edname = '\\'.join([filedir,frontname+'.mp4'])
        #print edname
        # (psped)付与
        if os.path.exists(edname):
            # ファイル名被った
            edname = os.path.join(filedir, ''.join([frontname, '(PSPed).mp4']))
        else:  # 被らなかった
            edname = os.path.join(filedir, ''.join([frontname, '(PSPed).mp4']))
        #print frontname.encode('cp932')
        # サムネ作成
        thmbnail = ''.join([os.path.splitext(edname)[0], '.jpg'])
        command = [self.ffmpeg,
                   u'-i', self.filename,
                   u'-f', u'image2',
                   u'-an',
                   u'-y',
                   u'-vframes', u'100',
                   u'-s', u'160x120',
                   thmbnail]
        command = [s.encode('cp932') for s in command]
        #print command
        print u'%sのサムネ作成.'%os.path.basename(self.filename)
        retcode = subprocess.call(command)

        # 動画変換
        command = [self.ffmpeg,
                   u'-y',
                   u'-i', self.filename,
                   u'-f', u'mp4',
                   u'-vcodec', u'libx264',
                   u'-coder', u'0',
                   u'-level', u'13',
                   u'-s', u'320x240',
                   u'-aspect', u'4:3',
                   u'-b', u'800k',
                   u'-bt', u'800k',
                   u'-crf', u'25', u'-mbd', u'2', u'-me_method', u'umh', u'-subq', u'6', u'-me_range', u'32', u'-keyint_min', u'3', u'-nr', u'100', u'-qdiff', u'4', u'-qcomp', u'0.60', u'-qmin', u'18', u'-qmax', u'51', u'-g', u'450', u'-sc_threshold', u'65', u'-flags', u'bitexact+alt+mv4+loop', u'-flags2', u'bpyramid+wpred+mixed_refs', u'-acodec', u'libfaac', u'-ac', u'2', u'-ar', u'44100', u'-ab', u'128k', u'-sn', u'-async', u'100',
                   edname]
        command = [s.encode('cp932') for s in command]
        #print command
        print u'%sを変換します.'%os.path.basename(self.filename)
        retcode = subprocess.call(command)

        try: self.sendmail()
        except: pass

        return retcode


        def sendmail(self):
            # メール送信
            from_addr = "*****@gmail.com"
            to_addr = "****@****"
            try:
                msg = gmail.create_message(from_addr, to_addr, "conversion end", self.filename)
            except:
                msg = gmail.create_message(from_addr, to_addr, "conversion end", u"変換終了")
            print u"send mail..."
            gmail.send_via_gmail(from_addr, to_addr, msg, "password")



"""
                   u'-f', u'psp',
                   u'-vcodec', u'libxvid',
                   u'-ab', u'64000',
                   u'-aspect', u'4:3',
"""
"""
                   u'-vcodec', u'libx264',
                   u'-coder', u'1',
                   u'-bufsize', u'128',
                   u'-g', u'250',
                   u'-s', u'360x270',
                   u'-b', u'1200k',
                   u'-r', u'30000/1001',
                   u'-acodec', u'libfaac',
                   u'-ar', u'44100',
                   u'-ab', u'128k',"""

if __name__ == '__main__':
    print 'START'

    # D&Dで開始
    converts = sys.argv

    if len(converts) > 1:
        converts.remove(converts[0])
        #print 'converts:',converts
        for i in converts:
            i = i.decode('mbcs')  ###
            ffmpeg = FFMpeg_convert(i)
            ffmpeg.main()
    print u'END'
    time.sleep(3)

'''iPod用設定
ffmpeg.exe -y -i "変換ファイル" -f mp4 -r 30000/1001 -vcodec libxvid -qscale 4 -ab 128k -maxrate 1500k -bufsize 4M -g 250 -coder 0 -threads 0 -acodec libfaac -ac 2 -aspect 352:200 -ar 44100 "C:demons縲代た繧ｦ繝ｫ菴薙▲縺ｦ縺昴ｓ縺ｪ繧ゅ�縺ｭ縲心ouls Mad縲�mp4"
'''

# -f mp4 -vcodec libx264 -coder 0 -level 13 -s 320x240 -aspect 4:3 -b 800k -bt 800k -crf 25 -mbd 2 -me_method umh -subq 6 -me_range 32 -keyint_min 3 -nr 100 -qdiff 4 -qcomp 0.60 -qmin 18 -qmax 51 -g 450 -sc_threshold 65 -flags bitexact+alt+mv4+loop -flags2 bpyramid+wpred+mixed_refs -acodec libfaac -ac 2 -ar 44100 -ab 128k -sn -async 100#!/usr/bin/env python
#-*- coding: utf-8 -*-

# 2012/02/14 譖ｴ譁ｰ

import os
import os.path
import subprocess
import sys,time

import sendgmail as gmail

class FFMpeg_convert():
    def __init__(self, filename):
        self.filename = os.path.abspath(filename)  # 変換ファイル名
        self.ffmpeg = ur'ffmpeg.exe'  # ffmpegの場所


    def main(self):
        frontname = os.path.basename(self.filename).split('.')[0]  # ファイル名特定
        filedir = os.path.dirname(self.filename)
        edname = '\\'.join([filedir,frontname+'.mp4'])
        #print edname
        # (psped)付与
        if os.path.exists(edname):
            # ファイル名被った
            edname = os.path.join(filedir, ''.join([frontname, '(PSPed).mp4']))
        else:  # 被らなかった
            edname = os.path.join(filedir, ''.join([frontname, '(PSPed).mp4']))
        #print frontname.encode('cp932')
        # サムネ作成
        thmbnail = ''.join([os.path.splitext(edname)[0], '.jpg'])
        command = [self.ffmpeg,
                   u'-i', self.filename,
                   u'-f', u'image2',
                   u'-an',
                   u'-y',
                   u'-vframes', u'100',
                   u'-s', u'160x120',
                   thmbnail]
        command = [s.encode('cp932') for s in command]
        #print command
        print u'%sのサムネ作成.'%os.path.basename(self.filename)
        retcode = subprocess.call(command)

        # 動画変換
        command = [self.ffmpeg,
                   u'-y',
                   u'-i', self.filename,
                   u'-f', u'mp4',
                   u'-vcodec', u'libx264',
                   u'-coder', u'0',
                   u'-level', u'13',
                   u'-s', u'320x240',
                   u'-aspect', u'4:3',
                   u'-b', u'800k',
                   u'-bt', u'800k',
                   u'-crf', u'25', u'-mbd', u'2', u'-me_method', u'umh', u'-subq', u'6', u'-me_range', u'32', u'-keyint_min', u'3', u'-nr', u'100', u'-qdiff', u'4', u'-qcomp', u'0.60', u'-qmin', u'18', u'-qmax', u'51', u'-g', u'450', u'-sc_threshold', u'65', u'-flags', u'bitexact+alt+mv4+loop', u'-flags2', u'bpyramid+wpred+mixed_refs', u'-acodec', u'libfaac', u'-ac', u'2', u'-ar', u'44100', u'-ab', u'128k', u'-sn', u'-async', u'100',
                   edname]
        command = [s.encode('cp932') for s in command]
        #print command
        print u'%sを変換します.'%os.path.basename(self.filename)
        retcode = subprocess.call(command)

        try: self.sendmail()
        except: pass

        return retcode


        def sendmail(self):
            # メール送信
            from_addr = "myremote717@gmail.com"
            to_addr = "tkhr-dan-ai@docomo.ne.jp"
            try:
                msg = gmail.create_message(from_addr, to_addr, "conversion end", self.filename)
            except:
                msg = gmail.create_message(from_addr, to_addr, "conversion end", u'変換完了')
            print u"send mail..."
            gmail.send_via_gmail(from_addr, to_addr, msg, "kusounkobaka")



"""
                   u'-f', u'psp',
                   u'-vcodec', u'libxvid',
                   u'-ab', u'64000',
                   u'-aspect', u'4:3',
"""
"""
                   u'-vcodec', u'libx264',
                   u'-coder', u'1',
                   u'-bufsize', u'128',
                   u'-g', u'250',
                   u'-s', u'360x270',
                   u'-b', u'1200k',
                   u'-r', u'30000/1001',
                   u'-acodec', u'libfaac',
                   u'-ar', u'44100',
                   u'-ab', u'128k',"""

if __name__ == '__main__':
    print 'START'

    # D&Dで開始
    converts = sys.argv

    if len(converts) > 1:
        converts.remove(converts[0])
        #print 'converts:',converts
        for i in converts:
            i = i.decode('mbcs')  ###
            ffmpeg = FFMpeg_convert(i)
            ffmpeg.main()
    print u'END'
    time.sleep(3)

'''iPod用設定
ffmpeg.exe -y -i "変換ファイル" -f mp4 -r 30000/1001 -vcodec libxvid -qscale 4 -ab 128k -maxrate 1500k -bufsize 4M -g 250 -coder 0 -threads 0 -acodec libfaac -ac 2 -aspect 352:200 -ar 44100 "C:demons縲代た繧ｦ繝ｫ菴薙▲縺ｦ縺昴ｓ縺ｪ繧ゅ�縺ｭ縲心ouls Mad縲�mp4"
'''

# -f mp4 -vcodec libx264 -coder 0 -level 13 -s 320x240 -aspect 4:3 -b 800k -bt 800k -crf 25 -mbd 2 -me_method umh -subq 6 -me_range 32 -keyint_min 3 -nr 100 -qdiff 4 -qcomp 0.60 -qmin 18 -qmax 51 -g 450 -sc_threshold 65 -flags bitexact+alt+mv4+loop -flags2 bpyramid+wpred+mixed_refs -acodec libfaac -ac 2 -ar 44100 -ab 128k -sn -async 100

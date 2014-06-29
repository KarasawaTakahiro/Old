# coding: utf-8

letter = '-f mp4 -vcodec libx264 -coder 0 -level 13 -s 320x240 -aspect 4:3 -b 800k -bt 800k -crf 25 -mbd 2 -me_method umh -subq 6 -me_range 32 -keyint_min 3 -nr 100 -qdiff 4 -qcomp 0.60 -qmin 18 -qmax 51 -g 450 -sc_threshold 65 -flags bitexact+alt+mv4+loop -flags2 bpyramid+wpred+mixed_refs -acodec libfaac -ac 2 -ar 44100 -ab 128k -sn -async 100'
letter = 'ffmpeg.exe -y -i "in" -f mp4 -r 30000/1001 -vcodec libxvid -qscale 4 -ab 128k -maxrate 1500k -bufsize 4M -g 250 -coder 0 -threads 0 -acodec libfaac -ac 2 -aspect 352:200 -ar 44100 output'
letters = letter.split()
ed = "', u'".join(letters)
ed=''.join(["u'", ed, "',"])
print ed
"""
count = 0
eded = ''
for item in ed:
    print item,
    eded = ''.join(eded, item)
    if item == ',':
        count += 1
    if count == 2:
        print '\n',
        eded = ''.join(eded, '\n')
        count = 0
"""
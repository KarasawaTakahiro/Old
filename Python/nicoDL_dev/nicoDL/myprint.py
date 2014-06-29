#!/usr/bin/env python
#-*- coding: utf-8 -*-

#import textwrap

class MyPrint():
    def __init__(self):
        self.Letter = u''  # 文字列
        self.Paragraph = None  # 段落フラグ
        self.Rule = None  # 罫線フラグ
        self.Path = None  # パス短縮フラグ
        self.Info = 0  # 段落情報
        self.Rule_preset = (u':', u'*', u'=', u'-')

    def myprint(self, letter=u'', paragraph=None, rule=None, rule_frequency=45, path=None, info=None):
        """
        letter 表示文字列
         罫線の記号指定も可
        paragraph 段落
         1  段落して表示
         0  同じ段落で表示
         -1 １つ戻す
         -2 段落を一時的に無視
         -3 段落リセット
        rule 罫線
         0  段落に従う
         -1 段落無視
        rule_frequency 罫線の長さ
        path パス短縮 (>= 1)
         値の数だけパスを両端から表示
         ただし、ドライブ名は常に表示
        info 段落情報
         外部とやり取り
        """
        self.Letter = letter
        if info != None:
            self.Info = info

        if paragraph != None:  # paragaph()
            if (paragraph == -1) or (paragraph == 0) or (paragraph == 1):
                #  paragraph が-1,0,1以外ならエラー
                self.paragraph(paragraph)
            else:
                raise ValueError

        if rule != None:
            self.rule(rule, rule_frequency)

        if path != None:
            self.path(path)


    def paragraph(self, flag):
        """
        flag
         1  段落して表示
         0  同じ段落で表示
         -1 １つ戻す
         -2 段落を一時的に無視
         -3 段落リセット
        """
        if flag == 1:
            self.Info += 1
            whitespace = u' ' * self.Info
            self.Letter = u''.join([whitespace, self.Letter])

        elif flag == 0:
            whitespace = u' ' * self.Info
            self.Letter = u''.join([whitespace, self.Letter])

        elif flag == -1:
            if self.Info != 0:
                self.Info = self.Info -1
            elif self.Info == 0:
                pass
            else:
                raise ValueError, u'Paragraph() flag = -1'

        elif flag == -2:
            pass

        elif flag == -3:
            self.Info = 0

        else:
            raise ValueError, u'Paragraph()'

        print self.Letter
        return self.Info

    def rule(self, flag, frequency):
        """
        flag
         0  段落に従う
         -1 段落無視

        fraquency 罫線の長さ
        """
        if flag == 0 or flag == -1:
            pass
        else:
            raise ValueError, u'rule()'
        info = self.Info

        # 記号選択
        if self.Letter == u'':
            if self.Info >= 4:  # プリセット以上の階層 or 段落無視
                sign = u'.'  # 罫線に使う文字
            elif flag == -1:
                sign = self.Rule_preset[0]
                info = 0
            else:
                sign = self.Rule_preset[info]
        else:
            sign = self.Letter

        # 文字列生成
        line = u''
        r = frequency - info
        if r < 1:  # 最低でも１つは表示
            r = 1
        for i in xrange(r):
            line = u''.join([line, sign])
        self.Letter = line

        # 表示
        if flag == 0:
            self.paragraph(flag=0)
        elif flag == -1:
            self.paragraph(flag=-2)

        del flag, sign, self.Letter

    def path(self, flag):
        """
        flag >= 1
         flagの数だけ両端から表示
         ただし、ドライブは除く
        """
        if flag == 0:
            raise ValueError, u'0以上の整数.'

        letters = []
        parts = self.Letter.split('\\')
        # ドライブ分離
        letters.append(parts[0])
        parts.remove(parts[0])

        length = len(parts)
        if flag > length/2:  # 足りない
            if flag == 1:
                pass
            else:
                raise ValueError, u'要求範囲で表示できません.'
        # 前半部
        for i in xrange(0, flag):
            letters.append(parts[0])
            parts.remove(parts[0])
        # 中間を除く
        length = len(parts)
        length = length - flag
        for i in xrange(0, length):
            parts.remove(parts[0])
        # 後半部
        if length != 0:
            letters.append(u'...')
        for i in parts:
            letters.append(i)
        # 接合 表示
        self.Letter = u'\\'.join(letters)
        self.paragraph(flag=0)

        del i, length, letters, parts



if __name__ == '__main__':
    import myprint
    m = MyPrint()
    m.myprint(u'ニコニコ動画ランキング',paragraph=0)
    m.myprint(u'ゆっくり実況プレイ', paragraph=1)
    letter = r'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\Temporary Files'
    m.myprint(letter, path=2)
    m.myprint(rule=-1)
    m.myprint(rule=0)
    m.Info += 1
    m.myprint(rule=0)
    m.Info += 1
    m.myprint(rule=0)
    m.Info += 1
    m.myprint(rule=0)
    m.Info += 1
    m.myprint(letter=u'+*.',rule=0)  ## 要検討

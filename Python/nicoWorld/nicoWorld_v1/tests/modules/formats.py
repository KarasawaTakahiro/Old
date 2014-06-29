
# coding: utf-8
'''
Created on 2012/02/29

@author: KarasawaTakahiro
'''

import os
import pickle


class LibraryFormat():
    """
    *保存ファイル名を指定しておく
    *パスは逐次指定する
    """
    def __init__(self, libraryfilepath=os.getcwd(), libraryfilename=u'Library.nco'):
        self.libraryfilepath = libraryfilepath
        self.libraryfilename = libraryfilename
        self.libraryfile = os.path.join(self.libraryfilepath, self.libraryfilename)
        #print '__init__:', self.libraryfilepath, self.libraryfilename
        self.library = {u'MOVIE' :{0:[],
                                   1:[],
                                   2:[],
                                   3:[],
                                   4:[],
                                   5:[],
                                   6:[],
                                   7:[],
                                   8:[],
                                   9:[],
                                  },
                        u'MYLIST':{0:[],
                                   1:[],
                                   2:[],
                                   3:[],
                                   4:[],
                                   5:[],
                                   6:[],
                                   7:[],
                                   8:[],
                                   9:[],
                                  } }

    def load(self):
        """
        return library obj
        *ライブラリをロード
        *self.libraryを上書き
        """
        if os.path.exists(self.libraryfile):
            # ライブラリファイルが見つかったらロード
            ff = open(self.libraryfile)
            try:
                self.library = pickle.load(ff)
            finally:  ff.close()
        else:
            print u'ライブラリファイルを新規作成'
            self.save()
        return self.library

    def save(self):
        """
        *保存
        """
        ff = open(self.libraryfile, 'w')
        try:  pickle.dump(self.library, ff)
        finally:  ff.close()

    def mkMovieFormat(self, ID, title=False, description=False,
                       path=False, size=False, 
                       thumbnail=False, state=False,
                       mylist_id=False):
        """
        form:        差別用
        below:       IDの下一桁
        ID:          動画ＩＤ
        title:       動画タイトル
        description: 動画説明
        path:        ローカルの保存パス
        size:        動画サイズ
        thumbnail:   サムネ保存パス
        state:       DL状態
        mylist_id:   マイリスID
        """
        return MovieFormat(ID=ID, title=title, description=description,
                       path=path, size=size, 
                       thumbnail=thumbnail, state=state,
                       mylist_id=mylist_id)

    def mkMylistFormat(self, ID, title=False,
                 description=False, rss=True,
                 catalog=[]):
        """
        form        :差別用    unicode
        below       :IDの下一桁    unicode
        ID          :マイリストID    unicode
        title        :マイリスト名    unicode
        description :マイリス説明    unicode
        rss         :RSSするか    bool
        catalog     :マイリストに含まれる動画リスト    list
        """
        return MylistFormat(ID, title=title,
                 description=description, rss=rss,
                 catalog=catalog)

    def checkOverlap(self, ID):
        """
        *重複チェック
        *return bool
        *被ったらTrue
        """
        if ID.find(u'sm') == 0:  mytype = u'MOVIE'
        else:  mytype = u'MYLIST'
        below = int(ID[-1])

        for item in self.library[mytype][below]:
            if item.ID == ID:
                return True
            else:  continue
        return False
    
    def append(self, obj):
        """
        obj: myformat object
        """
        print 'check:', self.checkOverlap(obj.ID)
        if self.checkOverlap(obj.ID):
            self.reset(obj)
        else:
            self.library[obj.type][obj.below].append(obj)
        # ソート
        if obj.type == 'MYLIST':  mycmp=self.mylistcmp
        else:  mycmp=self.moviecmp
        self.library[obj.type][obj.below].sort(cmp=mycmp)
        # 保存
        self.save()

    def reset(self, myformat):
        """
        stateをFalseにする
        movie,mylistどちらでも可
        """
        will = []  # 変更するやつ
        if myformat.type == 'MOVIE':
            will.append(myformat)
        elif myformat.type == 'MYLIST':
            # catalogに入っているすべてを対象にする
            for item in myformat.catalog:
                myform = self.getMovieMyform(movie_id=item)
                if myform.state == True:
                    will.append(myform)
        else: raise AttributeError, u'myformatのtypeが予想外です'
        for item in will:
            # 上書き
            self.rewrite(myformat=item, factor='state', value=False)

    def find(self, myformat):
        """
        myformatの子の中でのインデックスを返す
        """
        count = 0
        for data in self.library[myformat.type][myformat.below]:
            if data.ID == myformat.ID:
                return count
            else: count += 1
        else:
            raise ValueError, u'%sは見つかりませんでした' % myformat.ID

    def rewrite(self, myformat, factor, value, catalog=1):
        """
        
        catalog: factorにcatalogを指定したとき
                 0 -> 上書き
                 1 -> 追加
        """
        # 入ってた場所
        index = self.find(myformat)

        if factor == 'ID':
            myformat.ID = value
        elif factor == 'title':
            myformat.title = value
        elif factor == 'path':
            myformat.path = value
        elif factor == 'size':
            myformat.size = value
        elif factor == 'priority':
            myformat.priority = value
        elif factor == 'state':
            myformat.state = value
        elif factor == 'option':
            myformat.option = value
        elif factor == 'thumbnail':
            myformat.thumbnail = value
        elif factor == 'description':
            myformat.description = value
        elif factor == 'mylist_id':  # 動画の専用
            myformat.mylist_id = value
        elif factor == 'rss':
            myformat.rss = value
        elif factor == 'catalog':
            if not(type(value) == type([])):
                # valueがリストじゃないとき
                raise ValueError, u'valueはリスト'
            if catalog:
                # 追加
                myformat.catalog.extend(value)
            else:
                # 上書き
                myformat.catalog = value

        else:  raise ValueError, u'factorが存在しないか不正な値です。'

        # ライブラリ上書き
        self.library[myformat.type][myformat.below][index] = myformat
        #print u'%sの%sを%sに上書き_formats.rewrite' % (myformat.ID, factor, value)
        # 保存
        self.save()

    def getMovieMyformat(self, movie_id):
        """
        *動画IDでmyformatを見つける
        """
        myformats = self.getAllMovieMyformat()

        # 順番を逆にしたほうがはやい？
        if 5 <= int(movie_id[-1]) <= 9:
            myformats.reverse()

        for item in myformats:
            if item.ID == movie_id:
                # 見つかった
                # 元に戻す
                if 5 <= int(movie_id[-1]) <= 9:
                    myformats.reverse()
                return item
        raise ValueError, u'見つかりませんでした'

    def getMylistMyformat(self, mylist_id):
        """
        *マイリストIDでmyformatを見つける
        """
        myformats = self.getAllMylistMyformat()

        # 順番を逆にしたほうがはやい？
        if 5 <= int(mylist_id[-1]) <= 9:
            myformats.reverse()

        for item in myformats:
            if item.ID == mylist_id:
                # 見つかった
                # 元に戻す
                if 5 <= int(mylist_id[-1]) <= 9:
                    myformats.reverse()
                return item
        raise ValueError, u'見つかりませんでした'

    def getAllMovieMyformat(self):
        """
        *ライブラリに登録されているmyformatの動画のものを返す
        
        return list
        """
        myformats = []
        for count in xrange(0,10):
            libobj = self.load()
            myformats.extend(libobj['MOVIE'][count])
        return myformats

    def getAllMylistMyformat(self):
        """
        *ライブラリに登録されているmyformatのマイリスのものを返す
        
        return list
        """
        myformats = []
        for count in xrange(0,10):
            myformats.extend(self.load()['MYLIST'][count])
        return myformats

    def moviecmp(self, item1, item2):
        """ソート用"""
        return cmp(int(item1.ID[2:]), int(item2.ID[2:]))

    def mylistcmp(self, item1, item2):
        """ソート用"""
        return cmp(int(item1.ID), int(item2.ID))


class MovieFormat():
    def __init__(self, ID, title=False, description=False,
                       path=False, size=False, 
                       thumbnail=False, state=False,
                       mylist_id=False):
        """
        type      :差別用
        below     :IDの下一桁
        ID        :動画ＩＤ
        title     :動画タイトル
        path      :ローカルの保存パス
        size      :動画サイズ
        thumbnail :サムネ保存パス
        state     :DL状態
        mylist_id :マイリスID
        """
        self.type = u'MOVIE'
        self.below = int(ID[-1])

        self.ID = ID
        self.title = title
        self.description = description
        self.path = path
        self.size = size
        self.thumbnail = thumbnail
        self.state = state
        self.mylist_id = mylist_id

        self.priority = None
        self.option = None

    def __repr__(self):
        return u'MovieFormat.%s' % self.ID


class MylistFormat():
    def __init__(self, ID, title=False,
                 description=False, rss=True,
                 catalog=[]):
        """
        type        :差別用    unicode
        below       :IDの下一桁    unicode
        ID          :マイリストID    unicode
        title       :マイリスト名    unicode
        description :マイリス説明    unicode
        rss         :RSSするか    bool
        catalog     :マイリストに含まれる動画リスト    list
        fig         :マイリスに登録されている動画数
        """
        self.type = u'MYLIST'
        self.below = int(ID[-1])

        self.ID = ID
        self.title = title
        self.description = description
        self.rss = rss
        self.catalog = catalog
        self.catalog.extend(catalog)

        self.fig = len(self.catalog)  # 変数名は仮
        self.priority = None
        self.option = None
        
    def __repr__(self):
        return u'MylistFormat.%s' % self.ID


class InfoFormats():
    def __init__(self, infofiledir=os.getcwd(), infofile=u'info.nco'):
        self.infofile = os.path.join(infofiledir, infofile)
        self.gmail_id = u''
        self.gmail_pw = u''
        self.nico_id = u''
        self.nico_pw = u''
        self.toaddr = u''
        self.savedir = u''

    def mkCliantInfoFormat(self, gmail_id=u"", gmail_pw=u"",
                                 nico_id=u"", nico_pw=u"", 
                                 toaddr=u"", savedir=u'.'):
        self.gmail_id = gmail_id
        self.gmail_pw = gmail_pw
        self.nico_id = nico_id
        self.nico_pw = nico_pw
        self.toaddr = toaddr
        self.savedir = savedir
        return self

    def load(self):
        if not os.path.exists(self.infofile):
            # ファイルが見つからず
            print u'設定ファイルが見つかりませんでした。\n新規作成します。'
            info_obj = self.mkCliantInfoFormat()
        else:
            try:
                ff = open(self.infofile)
                info_obj = pickle.load(ff)
            finally:  ff.close()
        self.gmail_id = info_obj.gmail_id
        self.gmail_pw = info_obj.gmail_pw
        self.nico_id = info_obj.nico_id
        self.nico_pw = info_obj.nico_pw
        self.toaddr = info_obj.toaddr
        self.savedir = info_obj.savedir

        self.save()
        return self

    def save(self):
        try:
            ff = open(self.infofile, 'w')
            pickle.dump(self.mkCliantInfoFormat(gmail_id=self.gmail_id,
                                                gmail_pw=self.gmail_pw,
                                                nico_id=self.nico_id,
                                                nico_pw=self.nico_pw,
                                                toaddr=self.toaddr,
                                                savedir=self.savedir),
                       ff)
        finally:  ff.close()


if __name__ == '__main__':
    
    form = LibraryFormat(r'C:\Users\KarasawaTakahiro\workspace\nicoWorld\src\tests', 'Library.nco')
    """
    form.append(form.mkMovieFormat(ID='sm16267880'))
    form.append(form.mkMylistFormat(ID='16267880'))
    print form.getAllMovieMyformat()
    print form.getAllMylistMyformat()
    """
    #sm = form.getMovieMyformat('sm16267880')
    """
    for item in ['title', 'path', 'size', 'thumbnail', 'state', 'mylist_id', "description"]:
        form.rewrite(myformat=sm, factor=item, value=True)
    sm = form.getMovieMyformat('sm16267880')
    for item in ['title', 'path', 'size', 'thumbnail', 'state', 'mylist_id',]:
        print getattr(sm, item)
    """
    #sm = form.getMylistMyformat('16267880')
    """
    for item in ['title', 'state', 'rss', "description", 'catalog']:
        form.rewrite(myformat=sm, factor=item, value=[True])
    sm = form.getMylistMyformat('16267880')
    for item in ['title', 'state', 'rss', "description", 'catalog']:
        print item, getattr(sm, item)
        
    infof = InfoFormats()
    #formats = infof.mkCliantInfoFormat('gid','gpw','nid','npw', 'to', 'save')
    #infof.save()
    infof.load()
    for i in dir(infof):
        print i, getattr(infof, i)
    """
    """
    for i in dir(form.mkMovieFormat(ID='sm16267880')):
        if 0 <= i.find('_') <= 1:
            continue
        print i 
    """
    form.load()
    print form.library
    print form.getAllMovieMyformat()
    print form.checkOverlap('sm17034521')

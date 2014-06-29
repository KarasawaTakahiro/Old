
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
            except AttributeError:
                print u'ライブラリファイルを開けませんでした。\n新規作成します。'
                self.save()
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
        return _MovieFormat(ID=ID, title=title, description=description,
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
        return _MylistFormat(ID, title=title,
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
        #print 'check:', self.checkOverlap(obj.ID)
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
                myform = self.getMovieMyformat(movie_id=item)
                if myform.state == True:
                    will.append(myform)
        else: raise AttributeError, u'myformatのtypeが予想外です'
        for item in will:
            # 上書き
            self.rewrite(myformat=item, factor='state', value=False)
            #print item.ID, item.state

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
        raise ValueError, u'見つかりませんでした(%s)'%movie_id

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
            data = self.load()
            myformats.extend(data['MYLIST'][count])
        return myformats

    def remove(self, myformat):
        """指定したmyforatを削除する"""
        # マイリストに登録があるとき
        if myformat.type == 'MOVIE':
            # 動画の時
            if myformat.mylist_id:
                # マイリストから来ていたとき
                mylistf = self.getMylistMyformat(myformat.mylist_id)
                mylistf.catalog.remove(myformat.ID)
                mylistf.fig -= 1
        elif myformat.type == 'MYLIST':
            # マイリスの時
            for movie_id in myformat.catalog:
                movief = self.getMovieMyformat(movie_id)
                self.rewrite(movief, factor='mylist_id', value=False)
        else:  raise ValueError, u'myformatが異常'
        
        try:
            self.load()
            index = self.find(myformat)
            del self.library[myformat.type][myformat.below][index]
            self.save()
            return True
        except:
            return False

    def moviecmp(self, item1, item2):
        """ソート用"""
        return cmp(int(item1.ID[2:]), int(item2.ID[2:]))

    def mylistcmp(self, item1, item2):
        """ソート用"""
        return cmp(int(item1.ID), int(item2.ID))


class _MovieFormat():
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


class _MylistFormat():
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
    def __init__(self, infofiledir=os.getcwd(), infofilename=u'info.nco'):
        self.infofile = os.path.join(infofiledir, infofilename)
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


class WatcherFormats():
    def __init__(self, filedir, filename=u'watcher.nco'):
        self.filedir = filedir
        self.filename = filename
        self.fullpath = os.path.join(self.filedir, self.filename)
        # データ
        self.Data = _WatcherFormat()

    def load(self):
        """ロード"""
        if not os.path.exists(self.fullpath):
            # ファイルが見つからなかったら空で保存
            ff = open(self.fullpath, 'w')
            try:
                watcherformat = _WatcherFormat()
                pickle.dump(watcherformat, ff)
            finally:
                ff.close()

        ff = open(self.fullpath, 'r')
        self.Data = pickle.load(ff)
        ff.close()

        return self.Data

    def save(self):
        ff = open(self.fullpath, 'w')
        try:
            pickle.dump(self.Data, ff)
        finally:
            ff.close()

    def make_filefolder(self, folder, files=None):
        """ファイルとフォルダ登録用のひな形"""
        if not files:
            return {folder:{'files':list(), 'last':u''}}
        else:
            filelist = list()
            filelist.extend(files)
            return {folder:{'files':filelist, 'last':u''}}

    def append_software(self, path):
        """
        *再生用ソフトを登録
        """
        # 被りチェック
        try:  self.Data.software.index(path)
        except ValueError:
            # 被ってない
            self.Data.software.append(path)

    def append_library(self, dataformat):
        """ファイルを追加"""
        if type(dataformat) != dict:
            raise ValueError, u'format is different'
        folder = dataformat.keys()[0]
        files = dataformat[folder]['files']
        try:
            self.Data.library[folder]['files'].extend(files)
        except KeyError:
            # 新規登録
            self.Data.library.update(dataformat)

    def append_library2(self, dataformat):
        """self.append_libraryを被っていたら行わない"""
        folder = dataformat.keys()[0]
        files = dataformat[folder]['files']
        will = []
        for item in files:
            if self.checkfile(folder=folder, filename=item):
                will.append(item)
            else:  continue
        self.append_library(self.make_filefolder(folder, files=will))

    def append_ext(self, ext):
        # 被りチェック
        try:  self.Data.exts.index(ext)
        except ValueError:
            # 被ってないから追加
            self.Data.exts.append(ext)

    def remove_software(self, path):
        self.Data.software.remove(path)

    def remove_file(self, folder, filename):
        self.Data.library[folder]['file'].remove(filename)

    def remove_folder(self, path):
        del self.Data.library[path]

    def remove_ext(self, path):
        self.Data.exts.remove(path)

    def get_lib(self, folder):
        return self.Data.library[folder]['files']
        
    def set_lastfile(self, folder, filename):
        self.Data.library[folder]['lfile'] = os.path.split(filename)[-1]
        
    def checkfolder(self, folder):
        """folderがかぶったらFalse"""
        if not(folder in self.Data.library.keys()):
            return True
        else:
            return False
        
    def checkfile(self, folder, filename):
        """"""
        try:
            if not(os.path.split(filename) in self.Data.library[folder]['files']):
                return True
            else:
                return False
        except KeyError:
            return True


class _WatcherFormat():
    def __init__(self):
        """
        *登録したソフト  list"""
        self.software = []
        """ 登録したフォルダ、ファイル
        self.dataに保存
        {
        'folder':{'files':[], 'lfile':''}, 
        'folder':{'files':[], 'lfile':''},
        }
        """
        self.library = {}
        self.format = {u'files':[], u'lfile':u''}
        # 最後に選択したフォルダ
        self.lfolder = u''
        # 拡張子フィルタ
        self.exts = [u'mp4', u'flv']


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
    """
    form.load()
    print form.library
    print form.getAllMovieMyformat()
    print form.checkOverlap('sm17034521')
    """
    import sys
    senc = sys.getfilesystemencoding()
    mat = WatcherFormats('c:\\Users\\Dev\\Desktop', 'testdata.txt')
    mat.load()
    mat.append_software(r'C:\Program Files (x86)\GRETECH\GomPlayer\GOM.EXE'.decode(senc))
    for item in dir( mat.Data):
        print '%s:'%item, getattr(mat.Data, item)
    

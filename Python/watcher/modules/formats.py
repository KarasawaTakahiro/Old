
#coding: utf-8
"""
Created on 2012/03/19

@author: KarasawaTakahiro
"""

import os
import pickle
import sys

DUMPFILE = ur'watchelper.ndl'

class Formats(object):
    """
    """
    def __init__(self):
        """
        """
        self._softwares = []
        # 登録したソフト
        self._files = []  # [ ['folder', [file,,,,,], 'lastfile'], ]
        # 登録したファイル,フォルダ

        self._lsoftware = None
        # 最後に選択したソフト
        self._lfile = (None, None)# (folder, index)
        # 最後に再生したファイル

        self._exts = [u'.mp4', u'.flv']
        # 拡張子フィルター

    def load(self):
        """
        return
            softwares  : 登録されたソフト <List>
            files     : 登録されたファイル　フォルダのフルパスとともに <[[path<unicode>, files<list>],[],]> <list>
            lsoftware : 最後に選択されていたソフトのフルパス <unicode>
            lfile     : 最後に選択されていたファイルのフルパス <unicode>
            exts       : 拡張子フィルター <list>
        """
        if not(os.path.exists(DUMPFILE)):
            # ファイルが見つからなければ空の値を返す
            print u'見つからない'
            softwares = []
            files = []
            lsoftware = None
            lfile = None
            exts = self._exts
        else:
            ff = open(DUMPFILE)
            try:  data = pickle.load(ff)  # data == self
            finally:  ff.close()
    
            softwares = list(data._softwares)
    
            edfiles = []
            for item in data._files:
                #print 'item:', item
                try:
                    edfiles.append({'path':item['path'], 'files':list(item['files']), 'lastfile':item['lastfile']})
                except KeyError:
                    edfiles.append({'path':item['path'], 'files':list(item['files']), 'lastfile':u''})
            files = edfiles;  del edfiles

            if (len(data._softwares) == 0) or (data._lsoftware == None):
                lsoftware = None
            else:
                lsoftware = data._softwares[data._lsoftware]

            if (len(data._files) == 0) or (data._lfile == (None, None)):
                lfile = None
            else:
                lfile = os.path.join(data._files[data._lfile[0]]['path'], data._files[data._lfile[0]]['files'][data._lfile[1]])

            exts = data._exts
        
        self.softwares = softwares
        self.files = files
        self.lsoftware = lsoftware
        self.lfile = lfile
        self.exts = exts
        
        return {'softwares' : softwares,
                'files' : files,
                'lsoftware' : lsoftware,
                'lfile' : lfile,
                'exts' : exts,
                }

    def save(self, softwares, files, lsoftware, lfile, exts):
        """
        softwares  : 登録されたソフト <List>
        files     : 登録されたファイル　フォルダのフルパスとともに <[[path<unicode>, files<list>],[],]> <list>
        lsoftware : 最後に選択されていたソフトのフルパス <unicode>
        lfile     : 最後に選択されていたファイルのフルパス <unicode>
        exts      : 拡張子フィルター <list>
        """
        print 'save'
        print 'softwares:', softwares 
        print 'files:', files
        print 'lsoftware:', lsoftware
        print 'lfile:',lfile
        print 'exts:', exts
        self._mkformat(softwares, files, lsoftware, lfile, exts)
        ff = open(DUMPFILE.encode(sys.getfilesystemencoding()), 'w')
        try:
            pickle.dump(self, ff)
        finally:  ff.close()

    def _mkformat(self, softwares, files, lsoftware, lfile, exts):
        """
        softwares  : 登録されたソフト <List>
        files     : 登録されたファイル　フォルダのフルパスとともに <[[path<unicode>, files<list>],[],]> <list>
        lsoftware : 最後に選択されていたソフトのフルパス <unicode>
        lfile     : 最後に選択されていたファイルのフルパス <unicode>
        exts       : 拡張子フィルター <list>
        """
        softwares.sort()
        self._softwares = tuple(softwares)
        
        edfiles = []
        for item in files:
            item[1].sort()
            child = {'path':item[0], 'files':tuple(item[1]), u'lastfile':item[2]}
            edfiles.append(child)
        edfiles.sort()
        self._files = tuple(edfiles);  del edfiles

        index = 0
        for item in self._softwares:
            if item == lsoftware:
                break
            else:
                index += 1
                continue
        self._lsoftware = index;  del index

        #print 'lfile:', lfile
        flag = False
        index_folder = 0
        for item in self._files:
            index_file = 0
            #print 'item:',item
            for child in item['files']:
                #print 'child:',os.path.join(item['path'], child)
                if os.path.join(item['path'], child) == lfile:
                    ## 決定 ######
                    self._lfile = (index_folder, index_file)
                    #print '._lfile:', (index_folder, index_file)
                    flag = True
                    break
                else:  index_file += 1
            if flag:  break
            else:     index_folder += 1
        else:
            # 見つからなかった
            self._lfile = (None, None)
        
        list(exts).sort()
        self._exts = tuple(exts)


class Folders():
    """
    [(dirname, fullpath),,,]
    """
    def __init__(self, data=None):
        if data == None:
            self._folders = []
        elif not(type(self) == type(data)):
            raise ValueError, u'dataはFolderオブジェクト'
        else:
            self._folders = data._folders

        self._folders.sort(cmp=self._mycmp)

    def append(self, path):
        """
        path: fullpath
        """
        if type('') == type(path):
            path = path.decode(sys.getfilesystemencoding())
        self._folders.append((os.path.split(path)[-1], path))
        self._folders.sort(cmp=self._mycmp)
        return self._folders

    def remove(self, path):
        """
        path: 絶対パス、フォルダ名
        return -> bool
        """
        if os.path.isabs(path):
            pos = 1
        else: pos = 0

        for item in self._folders:
            # 見つかればTrue
            if item[pos] == path:
                self._folders.remove(item)
                return True
            else: continue
        # なければ
        return False

    def _mycmp(self, item1, item2):
        return cmp(item1[0], item2[0])

    def __repr__(self):
        return str(self._folders)


class Files():
    def __init__(self, data=None):
        if type(self) == type(data):
            self._files = data._files
        elif data == None: pass
        else: raise ValueError, u'dataはFilesオブジェクト'


if __name__ == '__main__':
    DUMPFILE = u'test_'+DUMPFILE
    form = Formats()
    print form
    data = form.laod()
    print data
    print
    form.save(softwares=[ur'c:\aaa.exe', ur'c:\bbb.exe'],
              files=[[ur'c:\movie', [u'テスト動画1.mp4',u'テスト動画2.mp4']], [ur'c:\mydoc\movies', [u'動画1.flv',u'動画2.flv',u'動画3.flv']]],
              lsoftware=ur'c:\bbb.exe',
              lfile=ur'c:\movie\テスト動画2.mp4',
              exts=[u'.mp4', u'.flv'])
    for item in dir(form):
        print item, getattr(form, item)
    print form._lsoftware
    data = form.laod()
    print data



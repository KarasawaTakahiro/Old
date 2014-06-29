
# coding: utf-8
'''
Created on 2012/02/29

@author: KarasawaTakahiro
'''

import os
import pickle


class LibraryFormat():
    """
    *�ۑ��t�@�C�������w�肵�Ă���
    *�p�X�͒����w�肷��
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
        *���C�u���������[�h
        *self.library���㏑��
        """
        if os.path.exists(self.libraryfile):
            # ���C�u�����t�@�C�������������烍�[�h
            ff = open(self.libraryfile)
            try:
                self.library = pickle.load(ff)
            except AttributeError:
                print u'���C�u�����t�@�C�����J���܂���ł����B\n�V�K�쐬���܂��B'
                self.save()
            finally:  ff.close()
        else:
            print u'���C�u�����t�@�C����V�K�쐬'
            self.save()
        return self.library

    def save(self):
        """
        *�ۑ�
        """
        ff = open(self.libraryfile, 'w')
        try:  pickle.dump(self.library, ff)
        finally:  ff.close()

    def mkMovieFormat(self, ID, title=False, description=False,
                       path=False, size=False, 
                       thumbnail=False, state=False,
                       mylist_id=False):
        """
        form:        ���ʗp
        below:       ID�̉��ꌅ
        ID:          ����h�c
        title:       ����^�C�g��
        description: �������
        path:        ���[�J���̕ۑ��p�X
        size:        ����T�C�Y
        thumbnail:   �T���l�ۑ��p�X
        state:       DL���
        mylist_id:   �}�C���XID
        """
        return _MovieFormat(ID=ID, title=title, description=description,
                       path=path, size=size, 
                       thumbnail=thumbnail, state=state,
                       mylist_id=mylist_id)

    def mkMylistFormat(self, ID, title=False,
                 description=False, rss=True,
                 catalog=[]):
        """
        form        :���ʗp    unicode
        below       :ID�̉��ꌅ    unicode
        ID          :�}�C���X�gID    unicode
        title        :�}�C���X�g��    unicode
        description :�}�C���X����    unicode
        rss         :RSS���邩    bool
        catalog     :�}�C���X�g�Ɋ܂܂�铮�惊�X�g    list
        """
        return _MylistFormat(ID, title=title,
                 description=description, rss=rss,
                 catalog=catalog)

    def checkOverlap(self, ID):
        """
        *�d���`�F�b�N
        *return bool
        *�������True
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
        # �\�[�g
        if obj.type == 'MYLIST':  mycmp=self.mylistcmp
        else:  mycmp=self.moviecmp
        self.library[obj.type][obj.below].sort(cmp=mycmp)
        # �ۑ�
        self.save()

    def reset(self, myformat):
        """
        state��False�ɂ���
        movie,mylist�ǂ���ł���
        """
        will = []  # �ύX������
        if myformat.type == 'MOVIE':
            will.append(myformat)
        elif myformat.type == 'MYLIST':
            # catalog�ɓ����Ă��邷�ׂĂ�Ώۂɂ���
            for item in myformat.catalog:
                myform = self.getMovieMyformat(movie_id=item)
                if myform.state == True:
                    will.append(myform)
        else: raise AttributeError, u'myformat��type���\�z�O�ł�'
        for item in will:
            # �㏑��
            self.rewrite(myformat=item, factor='state', value=False)
            #print item.ID, item.state

    def find(self, myformat):
        """
        myformat�̎q�̒��ł̃C���f�b�N�X��Ԃ�
        """
        count = 0
        for data in self.library[myformat.type][myformat.below]:
            if data.ID == myformat.ID:
                return count
            else: count += 1
        else:
            raise ValueError, u'%s�͌�����܂���ł���' % myformat.ID

    def rewrite(self, myformat, factor, value, catalog=1):
        """
        
        catalog: factor��catalog���w�肵���Ƃ�
                 0 -> �㏑��
                 1 -> �ǉ�
        """
        # �����Ă��ꏊ
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
        elif factor == 'mylist_id':  # ����̐�p
            myformat.mylist_id = value
        elif factor == 'rss':
            myformat.rss = value
        elif factor == 'catalog':
            if not(type(value) == type([])):
                # value�����X�g����Ȃ��Ƃ�
                raise ValueError, u'value�̓��X�g'
            if catalog:
                # �ǉ�
                myformat.catalog.extend(value)
            else:
                # �㏑��
                myformat.catalog = value

        else:  raise ValueError, u'factor�����݂��Ȃ����s���Ȓl�ł��B'

        # ���C�u�����㏑��
        self.library[myformat.type][myformat.below][index] = myformat
        #print u'%s��%s��%s�ɏ㏑��_formats.rewrite' % (myformat.ID, factor, value)
        # �ۑ�
        self.save()

    def getMovieMyformat(self, movie_id):
        """
        *����ID��myformat��������
        """
        myformats = self.getAllMovieMyformat()

        # ���Ԃ��t�ɂ����ق����͂₢�H
        if 5 <= int(movie_id[-1]) <= 9:
            myformats.reverse()

        for item in myformats:
            if item.ID == movie_id:
                # ��������
                # ���ɖ߂�
                if 5 <= int(movie_id[-1]) <= 9:
                    myformats.reverse()
                return item
        raise ValueError, u'������܂���ł���(%s)'%movie_id

    def getMylistMyformat(self, mylist_id):
        """
        *�}�C���X�gID��myformat��������
        """
        myformats = self.getAllMylistMyformat()

        # ���Ԃ��t�ɂ����ق����͂₢�H
        if 5 <= int(mylist_id[-1]) <= 9:
            myformats.reverse()

        for item in myformats:
            if item.ID == mylist_id:
                # ��������
                # ���ɖ߂�
                if 5 <= int(mylist_id[-1]) <= 9:
                    myformats.reverse()
                return item
        raise ValueError, u'������܂���ł���'

    def getAllMovieMyformat(self):
        """
        *���C�u�����ɓo�^����Ă���myformat�̓���̂��̂�Ԃ�
        
        return list
        """
        myformats = []
        for count in xrange(0,10):
            libobj = self.load()
            myformats.extend(libobj['MOVIE'][count])
        return myformats

    def getAllMylistMyformat(self):
        """
        *���C�u�����ɓo�^����Ă���myformat�̃}�C���X�̂��̂�Ԃ�
        
        return list
        """
        myformats = []
        for count in xrange(0,10):
            data = self.load()
            myformats.extend(data['MYLIST'][count])
        return myformats

    def remove(self, myformat):
        """�w�肵��myforat���폜����"""
        # �}�C���X�g�ɓo�^������Ƃ�
        if myformat.type == 'MOVIE':
            # ����̎�
            if myformat.mylist_id:
                # �}�C���X�g���痈�Ă����Ƃ�
                mylistf = self.getMylistMyformat(myformat.mylist_id)
                mylistf.catalog.remove(myformat.ID)
                mylistf.fig -= 1
        elif myformat.type == 'MYLIST':
            # �}�C���X�̎�
            for movie_id in myformat.catalog:
                movief = self.getMovieMyformat(movie_id)
                self.rewrite(movief, factor='mylist_id', value=False)
        else:  raise ValueError, u'myformat���ُ�'
        
        try:
            self.load()
            index = self.find(myformat)
            del self.library[myformat.type][myformat.below][index]
            self.save()
            return True
        except:
            return False

    def moviecmp(self, item1, item2):
        """�\�[�g�p"""
        return cmp(int(item1.ID[2:]), int(item2.ID[2:]))

    def mylistcmp(self, item1, item2):
        """�\�[�g�p"""
        return cmp(int(item1.ID), int(item2.ID))


class _MovieFormat():
    def __init__(self, ID, title=False, description=False,
                       path=False, size=False, 
                       thumbnail=False, state=False,
                       mylist_id=False):
        """
        type      :���ʗp
        below     :ID�̉��ꌅ
        ID        :����h�c
        title     :����^�C�g��
        path      :���[�J���̕ۑ��p�X
        size      :����T�C�Y
        thumbnail :�T���l�ۑ��p�X
        state     :DL���
        mylist_id :�}�C���XID
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
        type        :���ʗp    unicode
        below       :ID�̉��ꌅ    unicode
        ID          :�}�C���X�gID    unicode
        title       :�}�C���X�g��    unicode
        description :�}�C���X����    unicode
        rss         :RSS���邩    bool
        catalog     :�}�C���X�g�Ɋ܂܂�铮�惊�X�g    list
        fig         :�}�C���X�ɓo�^����Ă��铮�搔
        """
        self.type = u'MYLIST'
        self.below = int(ID[-1])

        self.ID = ID
        self.title = title
        self.description = description
        self.rss = rss
        self.catalog = catalog
        self.catalog.extend(catalog)

        self.fig = len(self.catalog)  # �ϐ����͉�
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
            # �t�@�C���������炸
            print u'�ݒ�t�@�C����������܂���ł����B\n�V�K�쐬���܂��B'
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
        # �f�[�^
        self.Data = None

    def load(self):
        """���[�h"""
        if not os.path.exists(self.fullpath):
            # �t�@�C����������Ȃ��������ŕۑ�
            ff = open(self.fullpath, 'w')
            pickle.dump(_WatcherFormat(), ff)
            ff.close()

        ff = open(self.fullpath, 'r')
        self.data = pickle.load(ff)
        ff.close()

        return self.data

    def save(self):
        ff = open(self.fullpath, 'w')
        try:
            pickle.dump(self.data, ff)
        finally:
            ff.close()

    def mkFormat(self, software, data, lfolder, exts):
        """ 
        software: List or unicode
        data: 
        lfolder: 
        exts: 
        """
        # �\�t�g�o�^
        software = []
        if type(software) == list:
            software.extend(software)
        else:
            software.append(software)
            
        #�f�[�^�o�^
        
    def append_software(self, path):
        """
        *�Đ��p�\�t�g��o�^
        """
        if self.Data == None:  raise ValueError, u'���[�h���Ă�������'

        # ���`�F�b�N
        try:  self.Data.software.index(path)
        except ValueError:
            # ����ĂȂ�
            self.Data.software.append(path)

    def append_file(self, folder, filename):
        """�t�@�C����ǉ�"""
        if self.Data == None:  raise ValueError, u'���[�h����'
        self.Data.data[folder]['files'].append(filename)

    def append_ext(self, ext):
        if self.Data == None:  raise ValueError, u'���[�h����'

        # ���`�F�b�N
        try:  self.Data.exts.index(ext)
        except ValueError:
            # ����ĂȂ�����ǉ�
            self.Data.exts.append(ext)

    def remove_software(self, path):
        self.Data.software.remove(path)

    def remove_file(self, folder, filename):
        self.Data.data[folder]['file'].remove(filename)

    def remove_folder(self, path):
        del self.Data.data[path]

    def remove_ext(self, path):
        self.Data.exts.remove(path)


class _WatcherFormat():
    def __init__(self):
        """
        *�o�^�����\�t�g  list"""
        self.software = []
        """ �o�^�����t�H���_�A�t�@�C��
        self.data�ɕۑ�
        {
        'folder':{'files':[], 'lfile':''}, 
        'folder':{'files':[], 'lfile':''},
        }
        """
        self.data = {}
        self.format = {u'files':[], u'lfile':u''}
        # �Ō�ɑI�������t�H���_
        self.lfolder = u''
        # �g���q�t�B���^
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
    form.load()
    print form.library
    print form.getAllMovieMyformat()
    print form.checkOverlap('sm17034521')


#coding: utf8
'''
Created on 2012/05/14

@author: Dev
'''

import modules.formats as Formats


data = {
"c:\\aaa":{'file':['a_0', 'a_1', 'a_2', 'a_3', 'a_4', 'a_5', 'a_6', 'a_7', 'a_8', 'a_9',],
            'last':''
            },
"c:\\bbb":{'file':['b_0', 'b_1', 'b_2', 'b_3', 'b_4', 'b_5', 'b_6', 'b_7', 'b_8', 'b_9',],
            'last':''
            },
"c:\\ccc":{'file':['c_0', 'c_1', 'c_2', 'c_3', 'c_4', 'c_5', 'c_6', 'c_7', 'c_8', 'c_9',],
            'last':''
            },
"c:\\ddd":{'file':['d_0', 'd_1', 'd_2', 'd_3', 'd_4', 'd_5', 'd_6', 'd_7', 'd_8', 'd_9',],
            'last':''
            },
"c:\\eee":{'file':['e_0', 'e_1', 'e_2', 'e_3', 'e_4', 'e_5', 'e_6', 'e_7', 'e_8', 'e_9',],
            'last':''
            },
}
import sys
senc = sys.getfilesystemencoding()
mat = Formats.WatcherFormats('c:\\Users\\Dev\\Desktop', 'testdata.txt')
mat.append_software(r'C:\Program Files (x86)\GRETECH\GomPlayer\GOM.EXE'.decode(senc))
for folder in data:
    print 'folder:', folder
    for filename in data[folder]['file']:
        mat.append_file(folder, filename)
for item in dir( mat.Data):
    print '%s:'%item, getattr(mat.Data, item)







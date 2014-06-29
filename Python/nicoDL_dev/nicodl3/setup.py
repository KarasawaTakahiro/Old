#! c:/Python26/python.exe
# -*- coding: utf-8 -*- 

from distutils.core import setup
import py2exe

option = {
    "compressed"    :    1    ,
    "optimize"      :    2    ,
    "bundle_files"  :    2
}

setup(
    options = {
        "py2exe"    :    option
    },

    windows = [
        {"script"   :    "nicoDL_main.pyw",
         "icon_resources":[(1,"data\\nicodl.ico")]
        }
    ],

    zipfile = None
)

#! c:/Python26/python.exe
# -*- coding: utf-8 -*-

import sys
from distutils.core import setup
import py2exe

option = {
    "compressed"    :    1    ,
    "optimize"      :    2    ,
    "bundle_files"  :    2
}

setup(
    options = {
        "py2exe"    :    option,
    },
    data_files=[('',['nicodl.ico'])],

    console = [
        {"script"   :    "nicoDL.py",
         "icon_resources":[(1,"nicodl.ico")]
        }
    ],

    zipfile = None
)
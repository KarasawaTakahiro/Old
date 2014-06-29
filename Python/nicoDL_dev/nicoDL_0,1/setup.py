#! c:/Python26/python.exe
# -*- coding: utf-8 -*-

import sys
from distutils.core import setup
import py2exe
import email

option = {
    "compressed"    :    1    ,
    "optimize"      :    2    ,
    "bundle_files"  :    2
}

setup(
    options = {
        "py2exe"    :    option,
    },

    windows = [
        {"script"   :    "nicoDL.py",
         "icon_resources":[(1,"nicodl.ico")]
        }
    ],

    zipfile = None
)
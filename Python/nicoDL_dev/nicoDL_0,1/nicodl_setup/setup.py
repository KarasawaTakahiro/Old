#! c:/Python26/python.exe
# -*- coding: utf-8 -*-

import sys
from distutils.core import setup
import py2exe


option = {
    "compressed"    :    1    ,
    "optimize"      :    2    ,
    "bundle_files"  :    1
}

setup(
    options = {
        "py2exe"    :    option,
    },

    console = [
        {"script"   :    "nicodl_setup.py",
        }
    ],

    zipfile = None
)
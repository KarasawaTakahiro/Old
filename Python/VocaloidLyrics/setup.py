# coding: utf-8

from distutils.core import setup
import py2exe

py2exe_options = {
  "compressed": 1,
  "optimize": 2,
  "bundle_files": 2}

setup(
  options = {"py2exe": py2exe_options},
  windows = [
    {"script" : "main.py", "icon_resources": [(1,"vocaloidLyrics.ico")]}],
  zipfile = None)

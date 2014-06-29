#!/usr/bin/env python
# coding: utf-8

import os
import os.path

def main():
    pathlist = []
    if os.path.exists(r"C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\Temporary Files"):
        pathlist.append(r"C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\Temporary Files")
    if os.path.exists(r"E:\Takahiro\niconico"):
        pathlist.append(r"E:\Takahiro\niconico")
    for path in pathlist:
        for dirpath, dirnames, filenames in os.walk(path):
            if filenames.rfined('.mp4') or filenames.rfined('.flv'):


if __name__ == '__main__':
    main()

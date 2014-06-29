# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import shutil

directory = os.getcwd()
before = directory + "\\before"
after = directory + "\\after"
origine = directory + "\\origine"
fno = 1
sno = 1

items = []

for items in os.walk("before"):
    items = items[-1]
    print items

    for item in items:
        print item
        shutil.copy2(before + "\\" + item, origine)

        itemname = item.split(".")
        name = itemname[0]
        itemend = itemname[-1]

        cname = name + " " + str(fno) + "-" + str(sno) + "." + itemend

        os.rename(before + "\\" + item, after + "\\" + cname)

        sno += 1

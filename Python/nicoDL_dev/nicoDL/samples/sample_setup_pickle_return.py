#!/usr/bin/env python
#-*- coding: utf-8 -*-

import pickle

f = open('info.ndl')
info = pickle.load(f)
print info

print info['NICO_ID']

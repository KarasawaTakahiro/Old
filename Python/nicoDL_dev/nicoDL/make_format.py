#!/usr/bin/env python
#-*- coding: utf-8 -*-


class nicoDL_Various():
    def __init__(self):
        pass
    def mk_movie_f(self, movie_id, state, priority=-1,
                         movie_name=None, mylist_id=None, mylist_name=None, option=None):
        """
        動画フォーマット
        movie_id    : unicode 必須
        priority    : int
        state       : bool    必須
        movie_name  : unicode
        mylist_id   : unicode
        mylist_name : unicode
        option      : unicode

        format : 差別用
        """
        return {"format"      : "MOVIE",
                "movie_id"    : movie_id,
                "priority"    : priority,
                "state"       : state,
                "movie_name"  : movie_name,
                "mylist_id"   : mylist_id,
                "mylist_name" : mylist_name,
                "option"      : option,
                }

    def mk_mylist_f(self, mylist_id,
                          mylist_name=None, option=None):#, downloaded=None):
        """
        mylist_id   : unicode 必須
        mylist_name : unicode
        option      : unicode
        downloaded  : list

        format : 差別用
        """
        return {"format"      : "MYLIST",
                "mylist_id"   : mylist_id,
                "mylist_name" : mylist_name,
                "option"      : option,
                "downloaded"  : []
                }

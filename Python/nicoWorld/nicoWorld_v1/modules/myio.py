
#coding: utf-8
'''
Created on 2012/05/28

@author: Dev

データベースの入出力用のモジュール
'''

import sqlite3

class 

    connector = sqlite3.connect("sqlite_test.db")

    sql = "insert into test_table values('1','python')"
    connector.execute(sql)
    sql = "insert into test_table values('2','パイソン')"
    connector.execute(sql)
    sql = "insert into test_table values('3','ぱいそん')"
    connector.execute(sql)

    connector.commit()
    connector.close()

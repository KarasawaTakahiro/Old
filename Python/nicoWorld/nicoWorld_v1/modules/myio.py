
#coding: utf-8
'''
Created on 2012/05/28

@author: Dev

�f�[�^�x�[�X�̓��o�͗p�̃��W���[��
'''

import sqlite3

class 

    connector = sqlite3.connect("sqlite_test.db")

    sql = "insert into test_table values('1','python')"
    connector.execute(sql)
    sql = "insert into test_table values('2','�p�C�\��')"
    connector.execute(sql)
    sql = "insert into test_table values('3','�ς�����')"
    connector.execute(sql)

    connector.commit()
    connector.close()

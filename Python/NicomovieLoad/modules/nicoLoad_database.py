#!/usr/bin/python
# coding: utf-8

import sqlite3

class Database():
    def __init__(self, databaseFile="nicomovieload.db"):
        self.con = sqlite3.connect(databaseFile, isolation_level=None)

    def ctTable(self):
        errors = 0
        # movie table
        try:
            # state: 0:yet(default) 1:already
            self.con.execute("""create table movie (
            id              integer primary key not null,
            movieid         text,
            title           text,
            description     text,
            state           integer default 0,
            loadTime        text    default current_timestamp,
            path            text,
            comment         text,
            thumbnail       text,
            size            integer,
            length          integer
            );""")
            self.con.execute("create index movieIndex on movie (movieid);")
        except sqlite3.OperationalError:
            errors += 1
        # mylist table
        try:
            # rss: 1:do(default) 0:not
            self.con.execute("""create table mylist (
            id          integer primary key not null,
            mylistid    integer not null,
            title       text,
            description text,
            rss         integer default 1,
            recordTime  text    default current_timestamp
            );
            """)
            self.con.execute("create index mylistIndex on mylist (mylistid);")
        except sqlite3.OperationalError:
            errors += 1
        # mylist has movie
        try:
            self.con.execute("""create table mylist_has_movie (
            id         integer primary key not null,
            mylistid   integer not null,
            movieid    text    not null,
            recordTime text    default current_timestamp
            );""")
            self.con.execute("create index mylistHasIndex on mylist_has_movie (mylistid);")
        except sqlite3.OperationalError:
            errors += 1
        # system
        try:
            self.con.execute("""create table queue (
            id       integer primary key not null,
            movieid  text not null
            );""")
        except sqlite3.OperationalError:
            errors += 1
        return errors

    # Movie
    def extMovieTable(self):
        """movie テーブルの存在を確認する"""
        num =  self.con.execute("select count (*) from sqlite_master where type='table' and name='movie';") 
        if num == 1: return True
        else: return False
    def extMovieidInTable(self, movieid):
        """
        movieidが存在したらTrue
        """
        if self.con.execute("select count (*) from movie where movieid == ?;", (movieid,)).fetchone()[0] > 0:
            return True
        else:
            return False
    def addMovie(self, movieid):
        if not self.extMovieidInTable(movieid):
            self.con.execute("insert into movie (movieid) values(?)", (movieid,))
            return True
        else: 
            #print "already exists"
            return False
    def setMovieTitle(self, movieid, title):
        self.con.execute("update movie set title = ? where movieid == ?;", (title, movieid,))
    def setMovieDescription(self, movieid, desc):
        self.con.execute("update movie set description = ? where movieid == ?;", (desc, movieid,))
    def setMovieState(self, movieid, state):
        self.con.execute("update movie set state = ? where movieid == ?;", (state, movieid,))
    def setMovieThumbnail(self, movieid, thumbnailPath):
        self.con.execute("update movie set thumbnail = ? where movieid == ?;", (thumbnailPath, movieid,))
    def setMoviePath(self, movieid, moviePath):
        self.con.execute("update movie set path = ? where movieid == ?;", (moviePath, movieid,))
    def setMovieSize(self, movieid, movieSize):
        self.con.execute("update movie set size = ? where movieid == ?;", (movieSize, movieid,))
    def getMovieId(self, movieid):  # データベース上のID
        cursor = self.con.cursor()
        cursor.execute("select id from movie where movieid == ?;",  (movieid,))
        return cursor.fetchone()[0]
    def getMovieTitle(self, movieid):
        cursor = self.con.cursor()
        cursor.execute("select title from movie where movieid == ?;", (movieid,))
        return cursor.fetchone()[0]
    def getMovieDescription(self, movieid):
        cursor = self.con.cursor()
        cursor.execute("select description from movie where movieid == ?;",  (movieid,))
        return cursor.fetchone()[0]
    def getMovieState(self, movieid):
        cursor = self.con.cursor()
        cursor.execute("select state from movie where movieid == ?;",  (movieid,))
        return cursor.fetchone()[0]
    def getMovieState0(self):
        cursor = self.con.cursor()
        cursor.execute("select movieid from movie where state == 0;")
        return cursor.fetchall()
    def getMovieLoadTime(self, movieid):
        """
        9時間の時差がある
        """
        cursor = self.con.cursor()
        cursor.execute("select loadTime from movie where movieid == ?;",  (movieid,))
        return cursor.fetchone()[0]
    def getMovieThumbnail(self, movieid):
        cursor = self.con.cursor()
        cursor.execute("select thumbnail from movie where movieid == ?;", (movieid,))
        return cursor.fetchone()[0]
    def getMoviePath(self, movieid):
        cursor = self.con.cursor()
        cursor.execute("select path from movie where movieid == ?;", (movieid,))
        return cursor.fetchone()[0]
    def getMovieSize(self, movieid):
        cursor = self.con.cursor()
        cursor.execute("select size from movie where movieid == ?;", (movieid,))
        return cursor.fetchone()[0]
    def getMovieLength(self, movieid):
        cursor = self.con.cursor()
        cursor.execute("select length from movie where movieid == ?;", (movieid,))
        return cursor.fetchone()[0]
    def rmMovie(self,  movieid):
        self.con.execute("delete from movie where movieid == ?;", (movieid,))

    # Mylist
    def extMylistTable(self):
        num =  self.con.execute("select count (*) from sqlite_master where type='table' and name='mylist';") 
        if num == 1: return True
        else: return False
    def extMylistInTable(self, mylistid):
        """テーブル内にmylistidが存在したらTrue"""
        if self.con.execute("select count (*) from mylist where mylistid == ?;", (mylistid,)).fetchone()[0] > 0:
            return True
        else: return False
    def addMylist(self, mylistid):
        if self.extMylistInTable():
            self.con.execute("insert into mylist(mylistid) values(?);", (mylistid,))
            return True
        else: 
            #print "already exists"
            return False
    def setMylistTitle(self, mylistid, title):
        self.con.execute("update mylist set title = ? where mylistid == ?;", (title, mylistid,))
    def setMylistDescription(self, mylistid, desc):
        self.con.execute("update mylist set description = ? where mylistid == ?;", (desc, mylistid,))
    def setMylistRss(self, mylistid, rss):
        self.con.execute("update mylist set rss = ? where mylistid == ?;", (rss, mylistid,))
    def getMylistAll(self):
        cursor = self.con.cursor()
        cursor.execute("select mylistid from mylist;")
        result = []
        for item in cursor.fetchall(): result.append(item[0])
        return result  # list
    def getMylistId(self, mylistid):  # データベースのID
        cursor = self.con.cursor()
        cursor.execute("select id from mylist where mylistid == ?;", (mylistid,))
        return cursor.fetchone()[0]
    def getMylistTitle(self, mylistid):
        cursor = self.con.cursor()
        cursor.execute("select title from mylist where mylistid == ?;", (mylistid,))
        return cursor.fetchone()[0]
    def getMylistDescription(self, mylistid):
        cursor = self.con.cursor()
        cursor.execute("select description from mylist where mylistid == ?;", (mylistid,))
        return cursor.fetchone()[0]
    def getMylistRss(self, mylistid):
        cursor = self.con.cursor()
        cursor.execute("select rss from mylist where mylistid == ?;", (mylistid,))
        return cursor.fetchone()[0]
    def getMylistRecordTime(self, mylistid):
        cursor = self.con.cursor()
        cursor.execute("select recordTime from mylist where mylistid == ?;", (mylistid,))
        return cursor.fetchone()[0]
    def rmMylist(self, mylistid):
        self.con.execute("delete from mylist where mylistid == ?;", (mylistid,))

    # mylist has movie
    def extMylistHasMovieTable(self):
        num =  self.con.execute("select count (*) from sqlite_master where type == 'table' and name == 'mylist_has_movie';") 
        if num == 1: return True
        else: return False
    def addMylistHasMovie(self, mylistid, movieid):
        if self.con.execute("select count (*) from mylist_has_movie where mylistid == ? and  movieid == ?;", (mylistid, movieid,)).fetchone()[0] == 0:
            self.con.execute("insert into mylist_has_movie(mylistid, movieid) values(?, ?);", (mylistid, movieid,))
            return True
        else:
            #print "already exists"
            return False
    def rmMylistHasMovie(self, mylistid, movieid):
        self.con.execute("delete from mylist_has_movie where mylistid == ? and movieid == ?;", (mylistid, movieid,))
    def getMylistHasMovieFromMylistid(self, mylistid):
        """
        マイリスIDからそのマイリスに含まれる動画IDを返す
        """
        cursor = self.con.cursor()
        cursor.execute("select movieid from mylist_has_movie where mylistid == ?;", (mylistid,))
        result = []
        for item in cursor.fetchall(): result.append(item[0])
        return result  # list
    def getMylistHasMovieFromMovieid(self, movieid):
        """
        動画IDが登録されているマイリスIDを返す
        """
        cursor = self.con.cursor()
        cursor.execute("select mylistid from mylist_has_movie where movieid == ?;", (movieid,))
        result = []
        for item in cursor.fetchall(): result.append(item[0])
        return result

    # queue
    def addQueue(self, movieid):
        self.con.execute("insert into queue (movieid) values(?);", (movieid,))
    def rmQueue(self, movieid):
        self.con.execute("delete from queue where movieid == ?;", (movieid,))
    def getQueueAll(self):
        cursor = self.con.cursor()
        cursor.execute("select movieid from queue order by id ;")
        result = []
        for item in cursor.fetchall(): result.append(item[0])
        return result


    def close(self):
        self.con.commit()
        self.con.close()

class SystemDatabase():
    def __init__(self, databaseFile="system.db"):
        self.con = sqlite3.connect(databaseFile, isolation_level=None)
    def ctTable(self):
        try:
            self.con.execute("""create table system (
            id      integer primary key not null,
            nicoid  text,
            nicopw  text,
            gmailid text,
            gmailpw text,
            savedir text
            );
            """)
            return True
        except sqlite3.OperationalError:
            return False
    def svNicoid(self, nicoid):
        print self.con.execute("select count (*) from system where id == 1;").fetchone()[0]
        if self.con.execute("select count (*) from system where id == 1;").fetchone()[0] == 0:
            self.con.execute("insert into system (nicoid) values (?);", (nicoid,))
        else:
            self.con.execute("update system set nicoid = ? where id == 1;", (nicoid,))
        return True
    def svNicopw(self, nicopw):
        if self.con.execute("select count (*) from system where id == 1;").fetchone()[0] == 0:
            self.con.execute("insert into system (nicopw) values (?);", (nicopw,))
        else:
            self.con.execute("update system set nicopw = ? where id == 1;", (nicopw,))
        return True
    def svGmailid(self, gmailid):
        if self.con.execute("select count (*) from system where id == 1;").fetchone()[0] == 0:
            self.con.execute("insert into system (gmailid) values (?);", (gmailid,))
        else:
            self.con.execute("update system set gmailid = ? where id == 1;", (gmailid,))
        return True
    def svGmailpw(self, gmailpw):
        if self.con.execute("select count (*) from system where id == 1;").fetchone()[0] == 0:
            self.con.execute("insert into system (gmailpw) values (?);", (gmailpw,))
        else:
            self.con.execute("update system set gmailpw = ? where id == 1;", (gmailpw,))
        return True
    def svSavedir(self, savedir):
        if self.con.execute("select count (*) from system where id == 1;").fetchone()[0] == 0:
            self.con.execute("insert into system (savedir) values (?);", (savedir,))
        else:
            self.con.execute("update system set savedir = ? where id == 1;", (savedir,))
            return True
    def getNicoid(self):
        cursor = self.con.cursor()
        cursor.execute("select nicoid from system where id == 1;")
        result = cursor.fetchone()
        if result == None: return ""
        else: return result[0]
    def getNicopw(self):
        cursor = self.con.cursor()
        cursor.execute("select nicopw from system where id == 1;")
        result = cursor.fetchone()
        if result == None: return ""
        else: return result[0]
    def getGmailid(self):
        cursor = self.con.cursor()
        cursor.execute("select gmailid from system where id == 1;")
        result = cursor.fetchone()
        if result == None: return ""
        else: return result[0]
    def getGmailpw(self):
        cursor = self.con.cursor()
        cursor.execute("select gmailpw from system where id == 1;")
        result = cursor.fetchone()
        if result == None: return ""
        else: return result[0]
    def getSavedir(self):
        cursor = self.con.cursor()
        cursor.execute("select savedir from system where id ==1;")
        result = cursor.fetchone()
        if result == None: return ""
        else: return result[0]
    def close(self):
        self.con.commit()
        self.con.close()


if __name__ == "__main__":
    """
    a = Database()
    a.ctTable()
    sm = "sm10"
    a.addMovie('sm10')
    a.setMovieTitle(sm, "テストタイ撮る")
    a.setMovieDescription(sm, "ｆｇらおｇんらえおいｇｒなえおなえｒ")
    a.setMovieState(sm, 1)
    a.setMovieThumbnail(sm, r"c:\ttt\aaa.png")
    a.setMoviePath(sm, "c:\downloads")
    a.setMovieSize(sm, 12334)
    print "MovieTitle:", a.getMovieTitle(sm)
    print "MovieDesc:", a.getMovieDescription(sm)
    print "MovieState:", a.getMovieState(sm)
    print "MovieLoadTime:", a.getMovieLoadTime(sm)
    print "MovieThumbnail:", a.getMovieThumbnail(sm)
    print "MoviePath:", a.getMoviePath(sm)
    print "MovieSize:", a.getMovieSize(sm)
    ml = "1000"
    a.addMylist("1000")
    a.setMylistTitle(ml, "テストマイリス")
    a.setMylistDescription(ml, "説明")
    a.setMylistRss(ml, 0)
    print "MylistId:", a.getMylistId(ml)
    print "MylistTitle:", a.getMylistTitle(ml)
    print "MylistDesc:", a.getMylistDescription(ml)
    print "MylistRss:", a.getMylistRss(ml)
    print "MylistRecord:", a.getMylistRecordTime(ml)
    a.addMylistHasMovie(ml, sm)
    a.addMylistHasMovie(ml, "sm11")
    a.addMylistHasMovie(ml, "sm12")
    a.addMylistHasMovie(ml, "sm13")
    a.addMylistHasMovie("2000", sm)
    print "fromMylist:", a.getMylistHasMovieFromMylistid(ml)
    print "fromMovie:", a.getMylistHasMovieFromMovieid(sm)
    a.close()
    """
    s = SystemDatabase()
    print s.ctTable()
    s.svNicoid("aaa@gmail.com")
    s.svNicopw("xxxxx")
    s.svGmailid("aaa@gmail.com")
    s.svGmailpw("vvvvv")
    s.svSavedir("c:\\dddd\\aaa")
    print s.getNicoid()
    print s.getNicopw()
    print s.getGmailid()
    print s.getGmailpw()
    print s.getSavedir()
    s.close()


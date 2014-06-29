# coding: utf-8

class LibraryFormat():
    u"""
    nicodl用フォーマット
    """
    def __init__(self, movie_id=False, movie_name=False,
                       movie_path=False, movie_size=False,
                       mylist_id=False, mylist_name=False,
                       mylist_description=False, rss=True,
                       state=False, priority=-1,
                       option=False, form=False,
                       downloaded=[]
                       ):
        u"""
        return myformat

        form               : MOVIE/MYLIST 差別用
        below              : int IDの下一桁
        movie_id           : unicode
        movie_name         : unicode
        movie_path         : unicode 動画ファイルパス
        movie_size         : unicode 動画サイズ
        mylist_id          : unicode
        mylist_name        : unicode
        mylist_description : unicode マイリス説明
        rss                : bool RSSするか
        priority           : int
        state              : bool DLしたか
        option             : unicode
        thumbnail          : unicode サムネ保存ディレクトリ

        movie_id か  mylist_idのどちらかは必須
        form == "MOVIE" or "MYLIST"
        """
        if movie_id != False or form == "MOVIE":
            form = "MOVIE"
            rss = False
            below = int(movie_id[-1])
        elif mylist_id != False or form=="MYLIST":
            form = "MYLIST"
            rss = True
            below = int(mylist_id[-1])
        else:
            raise ValueError, u"IDが入力されていません."

        self.form = form
        self.below = below

        self.movie_id = movie_id
        self.movie_name = movie_name
        self.movie_path = movie_path
        self.movie_size = movie_size
        self.thumbnail = False
        self.state = state

        self.mylist_id = mylist_id
        self.mylist_name = mylist_name
        self.mylist_description = mylist_description
        self.rss = rss
        self.downloaded = downloaded

        self.priority = priority
        self.option = option

    def __repr__(self):
        if self.form == "MOVIE":
            return "<LibraryFormat MOVIE.%s>" % self.movie_id
        elif self.form == "MYLIST":
            return "<LibraryFormat MYLIST.%s>" % self.mylist_id

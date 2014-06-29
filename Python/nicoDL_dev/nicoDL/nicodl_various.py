#!/usr/bin/env python
#-*- coding: utf-8 -*-

import nicovideo
import os
import pickle

class nicoDL_Various():
    def __init__(self):
        pass

    def make_myformat(self, movie_id=None, movie_name=None, movie_path=None, movie_size=None,
                            mylist_id=None, mylist_name=None, mylist_description=None, rss=True,
                            state=False, priority=-1, option=None,form=None
                            ):
        """
        return myformat

        フォーマット
        format             : MOVIE/MYLIST 差別用
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

        movie_id か mylist_id のどちらかは必須
        form == "MOVIE" or "MYLIST" 無くてもいい
        """
        if movie_id != None or form == "MOVIE":
            form = "MOVIE"
            rss = None
        elif mylist_id != None or form=="MYLIST":
            form = "MYLIST"
            rss = True
        elif movie_id == None and mylist_id == None:
            raise ValueError, u"idが入力されていません."
        else:
            return False

        return {"format"      : form,
                "movie_id"    : movie_id,
                "priority"    : priority,
                "state"       : state,
                "movie_name"  : movie_name,
                "mylist_id"   : mylist_id,
                "mylist_name" : mylist_name,
                "option"      : option,
                "downloaded"  : [],
                "mylist_description" :mylist_description,
                "rss"         : rss,
                "movie_path"  : movie_path,
                "movie_size"  : movie_size,
                "thumbnail"   : None
                }

    def write_library(self, myformat, libraryfiledir):
        """
        myformat       : myformat
        libraryfiledir : libraryファイルのあるディレクトリ(なければ作成する)

        library.ndl を開いてアイテムを追記していく
        """
        libraryfile = os.path.join(libraryfiledir, "library_ALL.ndl")
        #print libraryfile
        libraryfileexists = os.path.exists(libraryfile)

        if libraryfileexists == False:
            # ライブラリファイルがないとき
            items = []
            items.append(myformat)
            f = open(libraryfile, "w")
            pickle.dump(items, f)
            f.close()

        else:
            f = open(libraryfile, "r")
            items = pickle.load(f)
            f.close()
            items.append(myformat)
            f = open(libraryfile, "w")
            pickle.dump(items, f)
            f.close()

        return True

    def rewrite_library(self, key, value, libraryfilepath, movie_id=False, mylist_id=False):
        """
        key : 書き換える値のkey
        value : 書き換える値
        libraryfilepath : ライブラリファイルのパス
        movie_id, mylist_id : 参照 どちらか必要
        """
        if (movie_id == False) and (mylist_id == False):
            return False
        f = open(libraryfilepath)
        lib = pickle.load(f)
        f.close()
        c = 0
        #print lib
        for dic in lib:
            if (dic["format"] == "MYLIST") and (dic["mylist_id"] == mylist_id):
                #print dic
                # mylist を先に判定しないとダメ
                if key == "downloaded":
                    dic[key].append(value)
                else:
                    dic[key] = value
            elif (dic["format"] == "MOVIE") and (dic["movie_id"] == movie_id):
                #print dic
                dic[key] = value
            else:
                c += 1
                continue
            #print lib
            # 要素を入れなおす
            del lib[c]
            lib.insert(c, dic)
            del c
            break

        f = open(libraryfilepath, "w")
        pickle.dump(lib, f)
        f.close()


    def reflesh_libraryfile(self, libraryfile):
        f = open(libraryfile)
        data = pickle.load(f)
        f.close()
        for i in xrange(len(data)):
            try:
                data.remove(None)
            except ValueError:
                break
        data.reverse()
        f = open(libraryfile, "w")
        pickle.dump(data,f)
        f.close()

    def rsscheck(self, libraryfiledir):
        """
        ライブラリ内のマイリストについて
        webのマイリストと比較し未DL動画があればライブラリに追加

        libraryfiledir: ライブラリファイルのあるディレクトリのパス
        """
        f = open(os.path.join(libraryfiledir, "library_ALL.ndl"))
        items = pickle.load(f)
        f.close()
        for item in items:
            #print item["format"]
            if item["format"] == "MYLIST":
                if not item["mylist_description"] == None:
                    print u"RSS:", item["mylist_id"], item["mylist_description"]
                else:
                    print u"RSS:", item["mylist_id"]
                downloaded = item["downloaded"]
                try:
                    niconicovideo = nicovideo.Nicovideo(mylist_id=item["mylist_id"])
                except:  # 接続失敗
                    print u"ニコニコ動画に接続失敗..."
                    return False
                movies = niconicovideo.get_mylist_movies()
                #print movies
                for i in movies:
                    try:
                        downloaded.index(i)
                        continue
                    except ValueError:  # movie_id がdownloaded に 無い時
                        flag = True
                        for lib in items:
                            """
                            lib: myformat
                            i  : 追加したいmovie_id
                            forループで総当り
                            動画情報にHitしたらflagをFalse
                            forループを抜けた時点でflagがTrueのままならself.write_library()
                            """
                            if lib["movie_id"] == i:  # 動画情報にHit;ライブラリに登録済み
                                flag = False
                                break
                            else:  # 動画情報がない時
                                pass
                        if flag:
                            self.write_library(self.make_myformat(movie_id=i, mylist_id=item["mylist_id"],form="MOVIE"), libraryfiledir)
                            print u"RSSHit: ", i
                        continue
            else:
                continue



if __name__ == "__main__":
    va = nicoDL_Various()
    #va.write_library(va.make_myformat(mylist_id="999999"), os.path.join(os.getcwd(), "data"))
    #va.rewrite_library("downloaded", "sm999999", os.path.join(os.getcwd(), "data\\library_ALL.ndl"), mylist_id="999999")
    #print "End"
    #print
    #va.write_library(va.make_myformat(mylist_id="000000"), os.path.join(os.getcwd(), "data"))
    #f = open(os.path.join(os.getcwd(), "data\\library_ALL.ndl"))
    #d = pickle.load(f)
    #f.close()
    #va.rewrite_library("thumbnail", r'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\nicoDL_dev\nicoDL\data\thumbnail\12646949.jpeg', os.path.join(os.getcwd(), "data\\library_ALL.ndl"), movie_id="sm12646949")
    #f = open(os.path.join(os.getcwd(), "data\\library_ALL.ndl"))
    #d2 = pickle.load(f)
    #f.close()
    #print d
    #print d == d2
    #print "End"
    #print
    #va.reflesh_libraryfile(r'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\nicoDL_dev\nicoDL\data\library_ALL.ndl')
    va.rsscheck(r'C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\nicoDL_dev\nicoDL\data')


















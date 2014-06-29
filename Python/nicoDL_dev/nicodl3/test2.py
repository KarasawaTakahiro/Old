
import modules.nicodl_various as Various

various = Various.nicoDL_Various(r'.\data')

data = various.libopen()

for index in xrange(0,10):
    for item in data['MOVIE'][index]:
        if item.mylist_id == '30309865':
            print 'http://www.nicovideo.jp/watch/'+item.movie_id
            various.rewrite_library(factor='state', value=True, movie_id=item.movie_id)
            
            
            
            

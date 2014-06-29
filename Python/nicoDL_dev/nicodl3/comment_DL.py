# coding: utf-8

import modules.nicovideoAPI as nicoAPI
import modules.nicodl_various as Various

various = Various.nicoDL_Various('data')
nicovideo_id = 'zeuth717@gmail.com'
nicovideo_pw = 'kusounkobaka'

movieids = various.getmovieIDs()

for movieid in movieids:
    movieform = various.pickup(movieid)
    if movieform.movie_name == False:
        nicoapi = nicoAPI.Nicovideo(movie_id = movieid)
        various.rewrite_library(factor='movie_name', value=nicoapi.get_movie_title(), movie_id=movieid)
    if movieform.state == True:
        movie_name = various.pickup(movie_id=movieid, choice='movie_name')
        print movie_name
        nicoapi = nicoAPI.Nicovideo(movie_id=movieid)
        comm = nicoapi.get_comment(nicovideo_id, nicovideo_pw, 1000)
        ff = open(movie_name+'.xml', 'w')
        ff.write(comm)
        ff.close()




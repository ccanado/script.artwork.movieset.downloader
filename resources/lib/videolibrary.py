# import modules
import xbmc
import time
from datetime import timedelta

try:
    import json
    json.loads("[null]")
except:
    import simplejson as json

# import libraries
from resources.lib.utils import *
from resources.lib.database import Database

# get database class
DATABASE = Database()


### Define time took by an action
def time_took(t):
    return str(timedelta(seconds=(time.time() - t)))


### Define to get movie sets
def getMovieSets():
    st = time.time()
    postdata = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieSets", "params": {"properties": ["title"]}, "id": "1"}'
    s_json = xbmc.executeJSONRPC(postdata)
    try:
        s_json = string_unicode(s_json)
    except:
        pass
    o_json = json.loads(s_json).get('result', {})
    movie_sets = o_json.get('sets') or []
    log('VideoLibrary::getMovieSets took %r' % time_took(st))
    return movie_sets


### Define to get movie set first movie title
def getMovieSetFirstMovieTitle(idSet):
    st = time.time()
    postdata = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieSetDetails", "params": {"setid": %s, "movies": {"properties": ["title", "year"], "sort": {"order": "descending", "method": "year"}}}, "id": 1}' % idSet
    s_json = xbmc.executeJSONRPC(postdata)
    try:
        s_json = string_unicode(s_json)
    except:
        pass
    o_json = json.loads(s_json).get('result', {})
    movies = o_json['setdetails']['movies']
    first = movies[0]
    log('VideoLibrary::getMovieSetFirstMovieTitle took %r' % time_took(st))
    return '%s %s' % (first['title'], first['year'])


# Define to update set backdrop
def updateBackdropOfSet(idSet, backdrop):
    st = time.time()
    OK = False
    if idSet and backdrop:
        try:
            OK = DATABASE.commit("UPDATE art SET url=\"%s\" WHERE media_id=%i AND media_type=\"set\" AND type=\"fanart\"" % (backdrop, int(idSet)))
        except Exception, e:
            log(str(e), xbmc.LOGERROR)
        log('VideoLibrary::updateBackdropOfSet(%r, %r) took %r' % (idSet, backdrop, time_took(st)))
    return OK


# Define to update set poster
def updatePosterOfSet(idSet, poster):
    st = time.time()
    OK = False
    if idSet and poster:
        try:
            OK = DATABASE.commit("UPDATE art SET url=\"%s\" WHERE media_id=%i AND media_type=\"set\" AND type=\"poster\"" % (poster, int(idSet)))
        except Exception, e:
            log(str(e), xbmc.LOGERROR)
        log('VideoLibrary::updatePosterOfSet(%r, %r) took %r' % (idSet, poster, time_took(st)))
    return OK

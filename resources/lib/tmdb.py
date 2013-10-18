# import libraries
from resources.lib.utils import *

# constants
API_KEY = '4be68d7eab1fbd1b6fd8a3b80a65a95e'
BASE_API_URL = 'http://api.themoviedb.org'
API_COLLECTION_SEARCH = '/3/search/collection'
API_COLLECTION_INFO = '/3/collection'
API_MOVIE_SEARCH = '/3/search/movie'
API_MOVIE_INFO = '/3/movie'
BASE_IMAGE_URL = 'http://cf2.imgobject.com/t/p/'


### Get arts from collection name
def getArtsOfSet(collname, size='original'):
    log('TMDB API search criteria: Collection[''%s'']' % collname)
    collname = _cleanName(collname)

    total_results = 0
    tmdb_id = ''
    backdrop = ''
    poster = ''

    try:
        search_url = '%s%s?query=%s&api_key=%s' % (BASE_API_URL, API_COLLECTION_SEARCH, collname, API_KEY)
        log('TMDB API search: %s' % search_url)
        data = get_data(search_url, 'json')
        if data != "Empty":
            total_results = data['total_results']
            if total_results > 0:
                item = data['results'][0]
                tmdb_id = item['id']
                if item['backdrop_path']:
                    backdrop = '%s%s/%s' % (BASE_IMAGE_URL, size, item['backdrop_path'])
                if item['poster_path']:
                    poster = '%s%s/%s' % (BASE_IMAGE_URL, size, item['poster_path'])
    except Exception, e:
        log(str(e), xbmc.LOGERROR)
    if total_results == 0:
        log('TMDB API search found no ID')
    else:
        log('TMDB API search found %i results. We take ID: %s' % (total_results, tmdb_id))
    return tmdb_id, backdrop, poster


### Get arts from collection first movie to reset
def getArtsOfSetToReset(collname, size='original'):
    log('TMDB API search criteria: Collection[''%s'']' % collname)
    collname = _cleanName(collname)

    total_results = 0
    tmdb_id = ''
    backdrop = ''
    poster = ''

    try:
        search_url = '%s%s?query=%s&api_key=%s' % (BASE_API_URL, API_COLLECTION_SEARCH, collname, API_KEY)
        log('TMDB API search: %s' % search_url)
        data = get_data(search_url, 'json')
        if data != "Empty":
            total_results = data['total_results']
            if total_results > 0:
                item = data['results'][0]
                tmdb_id = item['id']

                search_url = '%s%s/%s?api_key=%s' % (BASE_API_URL, API_COLLECTION_INFO, tmdb_id, API_KEY)
                log('TMDB API search: %s' % search_url)
                data = get_data(search_url, 'json')
                if data != "Empty":
                    item = data['parts'][0]
                    if item['backdrop_path']:
                        backdrop = '%s%s/%s' % (BASE_IMAGE_URL, size, item['backdrop_path'])
                    if item['poster_path']:
                        poster = '%s%s/%s' % (BASE_IMAGE_URL, size, item['poster_path'])
    except Exception, e:
        log(str(e), xbmc.LOGERROR)
    if total_results == 0:
        log('TMDB API search found no ID')
    else:
        log('TMDB API search found %i results. We take ID: %s' % (total_results, tmdb_id))
    return tmdb_id, backdrop, poster


### Get arts from collection's movie name
def getArtsOfSetFromMovie(moviename, size='original'):
    log('TMDB API search criteria: Movie[''%s'']' % moviename)
    cleanmoviename = _cleanName(moviename[:-5])

    total_results = 0
    tmdb_id = ''
    backdrop = ''
    poster = ''
    backdrop_movie = ''
    poster_movie = ''

    try:
        # Call a seach about clean movie name
        search_url = '%s%s?query=%s&api_key=%s' % (BASE_API_URL, API_MOVIE_SEARCH, cleanmoviename, API_KEY)
        log('TMDB API search: %s' % search_url)
        data = get_data(search_url, 'json')
        if data != "Empty":
            total_results = data['total_results']

            # Get movie Id from one single result
            if total_results == 1:
                item = data['results'][0]
                tmdb_id = item['id']

            # Get movie Id from multiple result matching with title and year
            elif total_results > 1:
                for item in data['results']:
                    if (item['original_title'] == moviename[:-5]) and (item['release_date'][:4] == moviename[-4:]):
                        tmdb_id = item['id']

            # Call movie info by movie Id and get arts
            if tmdb_id != '':
                search_url = '%s%s/%s?api_key=%s' % (BASE_API_URL, API_MOVIE_INFO, tmdb_id, API_KEY)
                log('TMDB API search: %s' % search_url)
                data = get_data(search_url, 'json')
                if data != "Empty":
                    if data['backdrop_path']:
                        backdrop_movie = '%s%s/%s' % (BASE_IMAGE_URL, size, data['backdrop_path'])
                    if data['poster_path']:
                        poster_movie = '%s%s/%s' % (BASE_IMAGE_URL, size, data['poster_path'])

                    if data['belongs_to_collection']:
                        collection = data['belongs_to_collection']
                        tmdb_id = collection['id']
                        if collection['backdrop_path']:
                            backdrop = '%s%s/%s' % (BASE_IMAGE_URL, size, collection['backdrop_path'])
                        if collection['poster_path']:
                            poster = '%s%s/%s' % (BASE_IMAGE_URL, size, collection['poster_path'])
    except Exception, e:
        log(str(e), xbmc.LOGERROR)
    if total_results == 0:
        log('TMDB API search found no movie ID')
    else:
        log('TMDB API search found %i movie results. We take collection ID: %s' % (total_results, tmdb_id))
    return tmdb_id, backdrop, poster, backdrop_movie, poster_movie


### Clean name for TMDB searchs
def _cleanName(name):
    name = normalize_string(name)
    illegal_char = ' -<>:"/\|?*%'
    for char in illegal_char:
        name = name.replace(char, '+').replace('++', '+').replace('+++', '+')
    return name
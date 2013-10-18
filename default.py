#import modules
import xbmc
import xbmcaddon

# get addon info
__addon__ = xbmcaddon.Addon(id='script.artwork.movieset.downloader')
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__author__ = __addon__.getAddonInfo('author')
__version__ = __addon__.getAddonInfo('version')
__addonpath__ = __addon__.getAddonInfo('path')
__addonprofile__ = xbmc.translatePath(__addon__.getAddonInfo('profile')).decode('utf-8')
__icon__ = __addon__.getAddonInfo('icon')
__localize__ = __addon__.getLocalizedString

# import libraries
from resources.lib.utils import *
from resources.lib.videolibrary import *
from resources.lib.tmdb import *
from resources.lib.view import *


### Main Class
class Main:

    def __init__(self):
        # Get all moviesets
        dialog_msg('create', line1=__localize__(31201), background=False)
        collection = getMovieSets()

        # Iterate moviesets
        pos = 0
        backdrops_updated = 0
        posters_updated = 0
        for s in collection:
            pos += 1
            msg1 = s['title']
            msg2 = __localize__(31203) if __addon__.getSetting("reset_enabled") is True else __localize__(31202)
            if dialog_msg('iscanceled', True):
                break
            dialog_msg('update', percentage=int(float(pos) / float(len(collection)) * 100.0), line1=msg1, line2=msg2, background=False)

            if __addon__.getSetting("reset_enabled") is True:
                # Get arts from collection first movie name
                id, backdrop, poster = getArtsOfSetToReset(s['title'])
            else:
                # Get arts from collection name
                id, backdrop, poster = getArtsOfSet(s['title'])

            # If there is no results from TMDB
            if id == '':
                log('SEARCH %i:/%s/ - found no collection ID in TMDB' % (s['setid'], s['title']), xbmc.LOGNOTICE)

            # If there is arts, update it
            action = 'reseted' if __addon__.getSetting("reset_enabled") is True else 'updated'
            if updateBackdropOfSet(s['setid'], backdrop):
                backdrops_updated += 1
                log('SEARCH %i:/%s/ - Backdrop %s from %s' % (s['setid'], s['title'], action, id), xbmc.LOGNOTICE)
            if updatePosterOfSet(s['setid'], poster):
                posters_updated += 1
                log('SEARCH %i:/%s/ - Poster %s from %s' % (s['setid'], s['title'], action, id), xbmc.LOGNOTICE)

        # Show statics
        log('STATICS: %i movisets: %i backdrops and %i posters %s' % (len(collection), backdrops_updated, posters_updated, action), xbmc.LOGNOTICE)
        msg1 = __localize__(31205) % len(collection)
        msg2 = __localize__(31206) % (backdrops_updated, posters_updated)
        dialog_msg('close', False)
        dialog_msg('okdialog', line1=msg1, line2=msg2, background=True)


### Start of script
if (__name__ == '__main__'):
    log('######## Artwork MovieSet Downloader: Initializing...............................', xbmc.LOGNOTICE)
    log('## Add-on ID   = %s' % str(__addonid__), xbmc.LOGNOTICE)
    log('## Add-on Name = %s' % str(__addonname__), xbmc.LOGNOTICE)
    log('## Authors     = %s' % str(__author__), xbmc.LOGNOTICE)
    log('## Version     = %s' % str(__version__), xbmc.LOGNOTICE)
    Main()
    log('script stopped', xbmc.LOGNOTICE)

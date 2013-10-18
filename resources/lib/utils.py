#import modules
import xbmc
import xbmcaddon
import xbmcgui
import unicodedata
import urllib2

try:
    import json
    json.loads("[null]")
except:
    import simplejson as json

# get addon info
__addon__ = xbmcaddon.Addon(id='script.artwork.movieset.downloader')
__addonname__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')
__localize__ = __addon__.getLocalizedString

# import libraries
from urllib2 import HTTPError, URLError
from resources.lib.script_exceptions import *

# Declare dialog
dialog = xbmcgui.DialogProgress()


### Fixes unicode problems
def string_unicode(text, encoding='utf-8'):
    try:
        text = unicode(text, encoding)
    except:
        pass
    return text


def normalize_string(text):
    try:
        text = unicodedata.normalize('NFKD', string_unicode(text)).encode('ascii', 'ignore')
    except:
        pass
    return text


### Define log messages
def log(txt, severity=xbmc.LOGDEBUG):
    if severity == xbmc.LOGDEBUG and not __addon__.getSetting("debug_enabled") is 'true':
        pass
    else:
        try:
            message = ('%s: %s' % (__addonname__, txt))
            xbmc.log(msg=message, level=severity)
        except UnicodeEncodeError:
            try:
                message = normalize_string('%s: %s' % (__addonname__, txt))
                xbmc.log(msg=message, level=severity)
            except:
                message = ('%s: UnicodeEncodeError' % __addonname__)
                xbmc.log(msg=message, level=xbmc.LOGWARNING)


### Define dialogs
def dialog_msg(action,
               percentage=0,
               line0='',
               line1='',
               line2='',
               line3='',
               background=False,
               nolabel=__localize__(31102),
               yeslabel=__localize__(31101)):
    # Fix possible unicode errors
    line0 = line0.encode('utf-8', 'ignore')
    line1 = line1.encode('utf-8', 'ignore')
    line2 = line2.encode('utf-8', 'ignore')
    line3 = line3.encode('utf-8', 'ignore')

    # Dialog logic
    if not line0 == '':
        line0 = __addonname__ + line0
    else:
        line0 = __addonname__
    if not background:
        if action == 'create':
            dialog.create(__addonname__, line1, line2, line3)
        if action == 'update':
            dialog.update(percentage, line1, line2, line3)
        if action == 'close':
            dialog.close()
        if action == 'iscanceled':
            if dialog.iscanceled():
                return True
            else:
                return False
        if action == 'okdialog':
            xbmcgui.Dialog().ok(line0, line1, line2, line3)
        if action == 'yesno':
            return xbmcgui.Dialog().yesno(line0, line1, line2, line3, nolabel, yeslabel)
    if background:
        if (action == 'create' or action == 'okdialog'):
            if line2 == '':
                msg = line1
            else:
                msg = line1 + ': ' + line2
            xbmc.executebuiltin("XBMC.Notification(%s, %s, 7500, %s)" % (line0, msg, __icon__))


### Retrieve JSON data from site
def get_data(url, data_type='json'):
    data = []
    try:
        request = urllib2.Request(url)
        # TMDB needs a header to be able to read the data
        if url.startswith("http://api.themoviedb.org"):
            request.add_header("Accept", "application/json")
        req = urllib2.urlopen(request)
        if data_type == 'json':
            data = json.loads(req.read())
            if not data:
                data = 'Empty'
        else:
            data = req.read()
        req.close()
    except HTTPError, e:
        if e.code == 400:
            raise HTTP400Error(url)
        elif e.code == 404:
            raise HTTP404Error(url)
        elif e.code == 503:
            raise HTTP503Error(url)
        else:
            raise DownloadError(str(e))
    except URLError:
        raise HTTPTimeout(url)
    except socket.timeout, e:
        raise HTTPTimeout(url)
    except:
        data = 'Empty'
    return data

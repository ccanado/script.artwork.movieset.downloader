# import modules
import time
from glob import glob
from datetime import timedelta
from urllib import urlopen, quote_plus
from re import DOTALL, findall, search
import xbmc

sqlite3 = None
try:
    import sqlite3
except:
    pass

# import libraries
from resources.lib.utils import *

# Database Path
DB_PATHS = "".join(glob(xbmc.translatePath("special://Database/MyVideos*.db"))[-1:])


### Define time took by an action
def time_took(t):
    return str(timedelta(seconds=(time.time() - t)))


#xbmcdb = xbmc.executehttpapi
#executehttpapi cause Crash/SystemExit if multi addon running in backend!!!
# use urllib with xbmc.getIPAddress()
def getXbmcHttpBaseUrl():
    data = open(xbmc.translatePath("special://userdata/guisettings.xml")).read()
    webserver = search('<webserver>(.*?)</webserver>', data).group(1)
    password = search('<webserverpassword>(.*?)</webserverpassword>', data).group(1)
    port = search('<webserverport>(.*?)</webserverport>', data).group(1)
    username = search('<webserverusername>(.*?)</webserverusername>', data).group(1)
    xbmcHttp = "http://"
    if password and username:
        xbmcHttp += "%s:%s@" % (username, password)
        xbmcHttp += xbmc.getIPAddress()
    if port and port != "80":
        xbmcHttp += ":%s" % port
    xbmcHttp += "/xbmcCmds/xbmcHttp"
    return xbmcHttp


def xbmcdb(url, command, *params):
    source = ""
    try:
        params = ";".join(list(params))
        url += "?command=%s&parameter=%s" % (command, params)
        source = urlopen(url).read()
    except Exception, e:
        log(str(e), xbmc.LOGERROR)
    log('DataBase::url: %s' % url)
    log('DataBase::response: %r' % source)
    return source


### Fetch Records CLASS
class Records:

    def __init__(self):
        self.xbmcHttp = None
        self.idVersion = self.getVersion()
        if self.idVersion < 63:
            raise Exception('AMsD.DataBase: invalid database version: %r' % self.idVersion)

    def deprecatedCommit(self, sql):
        done = False
        try:
            if self.xbmcHttp is None:
                self.xbmcHttp = getXbmcHttpBaseUrl()
            done = ("done" in xbmcdb(self.xbmcHttp, "ExecVideoDatabase", quote_plus(sql)).lower())
        except Exception, e:
            log(str(e), xbmc.LOGERROR)
        return done

    def deprecatedFetch(self, sql, index=None):
        fields = []
        try:
            if self.xbmcHttp is None:
                self.xbmcHttp = getXbmcHttpBaseUrl()
            records = xbmcdb(self.xbmcHttp, "QueryVideoDatabase", quote_plus(sql))
            regexp = "<field>(.*?)</field>"
            if index is None:
                regexp *= 2
            fields = findall(regexp, records, DOTALL)
        except Exception, e:
            log(str(e), xbmc.LOGERROR)
        return fields

    def commit(self, sql):
        done = False
        committed = False
        if DB_PATHS and sqlite3:
            db = None
            try:
                db = sqlite3.connect(DB_PATHS, check_same_thread=False)
                done = bool(db.execute(sql).rowcount)
                if done:
                    db.commit()
                committed = True
            except Exception, e:
                log(str(e), xbmc.LOGERROR)
            if hasattr(db, "close"):
                db.close()
        if not committed:
            done = self.deprecatedCommit(sql)
        return done

    def fetch(self, sql, index=None):
        fields = []
        fetched = False
        if DB_PATHS and sqlite3:
            db = None
            try:
                db = sqlite3.connect(DB_PATHS, check_same_thread=False)
                records = db.execute(sql)
                if index == 0:
                    fields = records.fetchone()
                else:
                    fields = records.fetchall()
                fetched = True
            except Exception, e:
                log(str(e), xbmc.LOGERROR)
            if hasattr(db, "close"):
                db.close()
        if not fetched:
            fields = self.deprecatedFetch(sql, index)
        return fields

    def getVersion(self):
        try:
            return int(self.fetch("SELECT idVersion FROM version", index=0)[0])
        except:
            return 0


### Main database CLASS
class Database(Records):

    def __init__(self):
        Records.__init__(self)

    # EXAMPLES FOR THE FUTURE OF CUSTOM METHODS
    #
    # def getArt( self, mediaId, mediaType ):
    #     st = time.time()
    #     art = []
    #     try:
    #         sql = "SELECT type, url FROM art WHERE media_id=%i AND media_type='%s'" % ( int( mediaId ), mediaType )
    #         for t, u in self.fetch( sql ):
    #             if not u: continue
    #             try: u = "image://" + quote_plus( u.encode( "utf-8" ) )
    #             except:
    #                 try: u = "image://" + quote_plus( u )
    #                 except: pass
    #             art.append( ( t, u ) )
    #     except:
    #         print_exc()
    #     LOG( "xbmcart.getArt(%r, %r) took %r" % ( mediaId, mediaType, time_took( st ) ) )
    #     return dict( art )

    # def setArt( self, mediaId, mediaType, artType, url ):
    #     st = time.time()
    #     OK = False
    #     try:
    #         # check if exists
    #         sql = "SELECT art_id FROM art WHERE media_id=%i AND media_type='%s' AND type='%s'" % ( int( mediaId ), mediaType, artType )
    #         artId = self.fetch( sql, index=0 )
    #         if artId: # update
    #             sql = "UPDATE art SET url='%s' WHERE art_id=%i" % ( url, int( artId[ 0 ] ) )
    #         else: # insert
    #             sql = "INSERT INTO art(media_id, media_type, type, url) VALUES (%i, '%s', '%s', '%s')" % ( int( mediaId ), mediaType, artType, url )
    #         OK = self.commit( sql )
    #     except:
    #         print_exc()
    #     if mediaType in [ "actor", "director" ]:
    #         OK = self.setPeopleArt( mediaId, mediaType, artType, url )
    #     LOG( "xbmcart.setArt(%r, %r, %r, %r) took %r" % ( mediaId, mediaType, artType, url, time_took( st ) ) )
    #     return OK

    # def setPeopleArt( self, mediaId, mediaType, artType, url ):
    #     # switch media type
    #     mediaType = ( "actor", "director" )[ mediaType == "actor" ]
    #     OK = False
    #     try:
    #         sql = "SELECT type, art_id FROM art WHERE media_id=%i AND media_type='%s'" % ( int( mediaId ), mediaType )
    #         art = dict( [ ( t, i ) for t, i in self.fetch( sql ) ] )
    #         # check if exists
    #         artId = art.get( artType )
    #         if artId: # update
    #             sql = "UPDATE art SET url='%s' WHERE art_id=%i" % ( url, int( artId ) )
    #         else: # insert
    #             sql = "INSERT INTO art (media_id, media_type, type, url) VALUES (%i, '%s', '%s', '%s')" % ( int( mediaId ), mediaType, artType, url )
    #         OK = self.commit( sql )
    #     except:
    #         print_exc()
    #     return OK

    # def notValidMediaID( self, mediaId, mediaType ):
    #     media_id = -1
    #     try:
    #         table, col = TABLES[ mediaType ]
    #         sql = "SELECT %s FROM %s WHERE %s=%i" % ( col, table, col, int( mediaId ) )
    #         media_id = int( self.fetch( sql, index=0 )[ 0 ] )
    #     except:
    #         print_exc()
    #     return media_id != int( mediaId )

## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2009 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#
#    This file is part of Meresco Core.
#
#    Meresco Core is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Meresco Core is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Meresco Core; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
from merescocore.framework import Observable
from utils import insertHeader
from md5 import md5
from time import time
from random import randint
from urllib import urlencode
from urlparse import urlsplit
from cgi import parse_qs
from UserDict import UserDict

class TimedDictionary(object):
    def __init__(self, timeout):
        self._timeout = timeout
        self._dictionary = {}
        self._list = []

    def get(self, key, default=None):
        return self[key] if key in self else default

    def getTime(self, key):
        return self._dictionary[key][0]

    def purge(self):
        now = self._now()
        index = 0
        for i, key in enumerate(self._list):
            if self.hasExpired(key, now):
                del self._dictionary[key]
                index = i + 1
            else:
                break
        if index > 0:
            self._list = self._list[index:]

    def touch(self, key):
        self._dictionary[key] = (self._now(), self._dictionary[key][1])
        self._list.remove(key)
        self._list.append(key)

    def has_key(self, key):
        return key in self

    def hasExpired(self, key, time=None):
        if not time:
            time = self._now()
        return time > self.getTime(key) + self._timeout

    def _now(self):
        return time()

    def __getitem__(self, key):
        if self.hasExpired(key):
            del self[key]
        ignoredTime, value = self._dictionary.__getitem__(key)
        return value

    def __setitem__(self, key, value):
        self.purge()
        if key in self:
            self._list.remove(key)
        self._dictionary[key] = (self._now(), value)
        self._list.append(key)

    def __contains__(self, key):
        return key in self._dictionary

    def __delitem__(self, key):
        del self._dictionary[key]
        self._list.remove(key)

class Session(UserDict):
    def __init__(self, sessionId):
        d = {'id': sessionId}
        UserDict.__init__(self, d)

        self.lastUsedTime = time()

    def setLink(self, caption, key, value):
        return '<a href="?%s">%s</a>' % (urlencode({key: '+' + repr(value)}), caption)

    def unsetLink(self, caption, key, value):
        return '<a href="?%s">%s</a>' % (urlencode({key: '-' + repr(value)}), caption)

    def __cmp__(self, other):
        return type(self) == type(other) \
            and cmp(self.lastUsedTime, other.lastUsedTime) \
            or cmp(type(self), type(other))

class SessionHandler(Observable):
    def __init__(self, secretSeed, nameSuffix='', timeout=3600*2):
        Observable.__init__(self)
        self._secretSeed = secretSeed
        self._nameSuffix = nameSuffix
        self._sessions = {}
        self._sessionsList = []
        self._timeout = timeout

    def handleRequest(self, RequestURI='', Client=None, Headers={}, arguments = {}, *args, **kwargs):
        self._timeCutoff()

        sessioncookies = [cookie.strip() for cookie in Headers.get('Cookie','').split(';') if cookie.strip().startswith('session%s=' % self._nameSuffix)]
        sessionid, session = None, None
        if len(sessioncookies) >=1:
            sessionid = sessioncookies[0].split('=')[1]
            session = self._sessions.get(sessionid, None)

        if session == None:
            clientaddress, ignoredPort = Client
            sessionid = md5('%s%s%s%s' % (time(), randint(0, 9999999999), clientaddress, self._secretSeed)).hexdigest()
            session = Session(sessionid)
            self._sessions[sessionid] = session
            self._sessionsList.append(session)
        else:
            session.lastUsedTime = time()
            #self._sessionsList.sort()

        extraHeader = 'Set-Cookie: session%s=%s; path=/' % (self._nameSuffix, sessionid)

        result = self.all.handleRequest(session=session, arguments=arguments, RequestURI=RequestURI, Client=Client, Headers=Headers, *args, **kwargs)

        for response in insertHeader(result, extraHeader) :
            yield response

    def _timeCutoff(self):
        if self._sessionsList == []:
            return

        timeCutoff = time() - self._timeout
        cutoffIndex = None
        for i in xrange(0, len(self._sessionsList)):
            if self._sessionsList[i].lastUsedTime < timeCutoff:
                cutoffIndex = i
            else:
                break
        if cutoffIndex != None:
            for i in range(0, cutoffIndex+1):
                del self._sessions[self._sessionsList[i]['id']]
            del self._sessionsList[:cutoffIndex+1]

#steps:
#Generate some kind of unique id. bijv. md5(time() + ip + secret_seed)
#set the cookie name,value pairs
    #some kind of escaping
#request cookie must be taken into consideration (if existing, don't generate a new session)

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
from utils import CRLF
from md5 import md5
from time import time
from random import randint
from urllib import urlencode
from urlparse import urlsplit
from cgi import parse_qs
from UserDict import UserDict

class Session(UserDict):
    def __init__(self, sessionId):
        d = {'id': sessionId}
        UserDict.__init__(self, d)

    def setLink(self, caption, key, value):
        return '<a href="?%s">%s</a>' % (urlencode({key: '+' + repr(value)}), caption)

    def unsetLink(self, caption, key, value):
        return '<a href="?%s">%s</a>' % (urlencode({key: '-' + repr(value)}), caption)

class ArgumentsInSession(Observable):

    def handleRequest(self, session, arguments = {}, *args, **kwargs):
        for k,v in arguments.items():
            if not k in session:
                session[k] = []
            for arg in v:
                if arg[0] in '+-':
                    sign, source = arg[0], arg[1:]
                else:
                    sign = '+'
                    source = repr(arg)
                try:
                    value = eval(source, {'__builtins__': {}})
                except Exception, e:
                    yield 'HTTP/1.0 400 Bad Request\r\n\r\n' + str(e)
                    return
                if sign == '+':
                    if not value in session[k]:
                        session[k].append(value)
                elif sign == '-' and value in session[k]:
                        session[k].remove(value)
        yield self.all.handleRequest(session=session, *args, **kwargs)

class SessionHandler(Observable):
    def __init__(self, secretSeed, nameSuffix=''):
        Observable.__init__(self)
        self._secretSeed = secretSeed
        self._nameSuffix = nameSuffix
        self._sessions = {}

    def handleRequest(self, RequestURI='', Client=None, Headers={}, arguments = {}, *args, **kwargs):
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
        extraHeader = 'Set-Cookie: session%s=%s; path=/' % (self._nameSuffix, sessionid)

        result = self.all.handleRequest(session=session, arguments=arguments, RequestURI=RequestURI, Client=Client, Headers=Headers, *args, **kwargs)
        alreadyDone = False
        for iets in result:
            if not alreadyDone and CRLF in iets:
                alreadyDone = True
                heeliets = iets.split(CRLF, 1)
                yield heeliets[0] + CRLF
                yield extraHeader + CRLF
                yield heeliets[1]
            else:
                yield iets



#steps:
#Generate some kind of unique id. bijv. md5(time() + ip + secret_seed)
#set the cookie name,value pairs
    #some kind of escaping
#request cookie must be taken into consideration (if existing, don't generate a new session)

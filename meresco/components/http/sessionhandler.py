from meresco.framework import Observable
from utils import CRLF
from md5 import md5
from time import time
from random import randint
from urllib import urlencode
from urlparse import urlsplit
from cgi import parse_qs

class Session(object):
    def __init__(self, sessionId):
        self._data = {'id': sessionId}

    def __getattr__(self, name):
        return getattr(self._data)

    def get(self, *args, **kwargs):
        return self._data.get(*args, **kwargs)

    def __contains__(self, key):
        return key in self._data

    def __getitem__(self, key, defaultValue=None):
        return self._data.get(key, defaultValue)

    def __setitem__(self, key, value):
        self._data[key] = value

    def setLink(self, caption, key, value):
        return '<a href="?%s">%s</a>' % (urlencode({key: '+' + repr(value)}), caption)

    def unsetLink(self, caption, key, value):
        return '<a href="?%s">%s</a>' % (urlencode({key: '-' + repr(value)}), caption)

    def keys(self):
        return self._data.keys()

class SessionHandler(Observable):
    def __init__(self, secretSeed):
        Observable.__init__(self)
        self._secretSeed = secretSeed
        self._sessions = {}

    def handleRequest(self, RequestURI='', Client=None, Headers={}, arguments = {}, *args, **kwargs):
        sessioncookies = [cookie.strip() for cookie in Headers.get('Cookie','').split(';') if cookie.strip().startswith('session=')]
        sessionid, session = None, None
        if len(sessioncookies) >=1:
            sessionid = sessioncookies[0].split('=')[1]
            session = self._sessions.get(sessionid, None)
        if session == None:
            clientaddress, ignoredPort = Client
            sessionid = md5('%s%s%s%s' % (time(), randint(0, 9999999999), clientaddress, self._secretSeed)).hexdigest()
            session = Session(sessionid)
            self._sessions[sessionid] = session
        extraHeader = 'Set-Cookie: session=%s; path=/' % sessionid

        for k,v in arguments.items():
            if not k in session:
                session[k] = []
            for value in v:
                try:
                    sign, value = value[0], eval(value[1:], {'__builtins__': {}})
                except Exception, e:
                    yield 'HTTP/1.0 400 Bad Request\r\n\r\n' + str(e)
                    return
                if sign == '+':
                    session[k].append(value)
                elif sign == '-' and value in session[k]:
                        session[k].remove(value)

        result = self.all.handleRequest(session=session, RequestURI=RequestURI, Client=Client, Headers=Headers, *args, **kwargs)
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
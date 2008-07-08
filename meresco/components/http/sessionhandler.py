from meresco.framework import Observable
from utils import CRLF
from md5 import md5
from time import time
from random import randint

class SessionHandler(Observable):
    def __init__(self, secretSeed):
        Observable.__init__(self)
        self._secretSeed = secretSeed
        self._sessions = {}

    def handleRequest(self, Client=None, Headers={}, *args, **kwargs):
        sessioncookies = [cookie.strip() for cookie in Headers.get('Cookie','').split(';') if cookie.strip().startswith('session=')]
        sessionid, session = None, None
        if len(sessioncookies) >=1:
            sessionid = sessioncookies[0].split('=')[1]
            session = self._sessions.get(sessionid, None)
        if session == None:
            clientaddress, ignoredPort = Client
            sessionid = md5('%s%s%s%s' % (time(), randint(0, 9999999999), clientaddress, self._secretSeed)).hexdigest()
            session = {'id':sessionid}
            self._sessions[sessionid] = session
        extraHeader = 'Set-Cookie: session=%s; path=/' % sessionid
        result = self.all.handleRequest(session=session, Client=Client, Headers=Headers, *args, **kwargs)
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
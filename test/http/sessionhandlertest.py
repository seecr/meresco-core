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

from unittest import TestCase
from merescocore.components.http import SessionHandler, utils
from merescocore.components.http.sessionhandler import Session
from weightless import compose
from cq2utils import CallTrace
from time import time, sleep

#Cookies RFC 2109 http://www.ietf.org/rfc/rfc2109.txt
class SessionHandlerTest(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.handler = SessionHandler(secretSeed='SessionHandlerTest')
        self.observer = CallTrace('Observer')
        self.handler.addObserver(self.observer)

    def testCreateSession(self):
        called = []
        def handleRequest(*args, **kwargs):
            called.append({'args':args, 'kwargs':kwargs})
            yield  utils.okHtml
            yield '<ht'
            yield 'ml/>'
        self.observer.handleRequest = handleRequest
        result = ''.join(compose(self.handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345), Headers={'a':'b'})))

        self.assertEquals(1, len(called))
        session = called[0]['kwargs']['session']
        self.assertTrue(session)
        self.assertEquals({'a':'b'}, called[0]['kwargs']['Headers'])
        self.assertTrue(('127.0.0.1', 12345), called[0]['kwargs']['Client'])
        header, body = result.split(utils.CRLF*2,1)
        self.assertEquals('<html/>', body)
        self.assertTrue('Set-Cookie' in header, header)
        headerParts = header.split(utils.CRLF)
        self.assertEquals("HTTP/1.0 200 OK", headerParts[0])
        sessionCookie = [p for p in headerParts[1:] if 'Set-Cookie' in p][0]
        self.assertTrue(sessionCookie.startswith('Set-Cookie: session='))
        self.assertTrue(sessionCookie.endswith('; path=/'))
        self.assertEquals('Set-Cookie: session=%s; path=/' % session['id'], sessionCookie)

    def testCreateSessionWithName(self):
        self.handler = SessionHandler(secretSeed='SessionHandlerTest', nameSuffix='Mine')
        self.observer = CallTrace('Observer')
        self.handler.addObserver(self.observer)
        def handleRequest(*args, **kwargs):
            yield  utils.okHtml
            yield '<html/>'
        self.observer.handleRequest = handleRequest
        result = ''.join(compose(self.handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345))))
        header, body = result.split(utils.CRLF*2,1)
        self.assertTrue('Set-Cookie' in header, header)
        headerParts = header.split(utils.CRLF)
        self.assertEquals("HTTP/1.0 200 OK", headerParts[0])
        sessionCookie = [p for p in headerParts[1:] if 'Set-Cookie' in p][0]
        self.assertTrue(sessionCookie.startswith('Set-Cookie: sessionMine='), sessionCookie)

    def testRetrieveCookie(self):
        sessions = []
        def handleRequest(session=None, *args, **kwargs):
            sessions.append(session)
            yield  utils.okHtml + '<html/>'
        self.observer.handleRequest = handleRequest
        result = ''.join(compose(self.handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345), Headers={})))
        result = ''.join(compose(self.handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345), Headers={'Cookie': 'session=%s' % sessions[0]['id']})))
        self.assertEquals(sessions[0], sessions[1])
        self.assertEquals(id(sessions[0]),id(sessions[1]))

    def testInjectAnyCookie(self):
        sessions = []
        def handleRequest(session=None, *args, **kwargs):
            sessions.append(session)
            yield  utils.okHtml + '<html/>'
        self.observer.handleRequest = handleRequest
        result = ''.join(compose(self.handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345), Headers={'Cookie': 'session=%s' % 'injected_id'})))
        self.assertNotEqual('injected_id', sessions[0]['id'])

    def testSetSessionVarsWithLink(self):
        arguments = {}
        def handleRequest(session=None, *args, **kwargs):
            arguments.update(kwargs)
            yield session.setLink('setvalue', 'key', 'value1')
            yield session.unsetLink('unsetvalue', 'key', 'value2')
        self.observer.handleRequest = handleRequest
        result = ''.join(compose(self.handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345), Headers={})))
        self.assertEquals(  '<a href="?key=%2B%27value1%27">setvalue</a>' +
                            '<a href="?key=-%27value2%27">unsetvalue</a>', result)

    def testSimpleDataTypeArgumentsViaURL(self):
        def handleRequest(session=None, *args, **kwargs):
            yield session.setLink('linktitle', 'key', ('a simple tuple',))
        self.observer.handleRequest = handleRequest
        result = ''.join(compose(self.handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345), Headers={})))
        self.assertEquals("""<a href="?key=%2B%28%27a+simple+tuple%27%2C%29">linktitle</a>""", result)

    def assertSessionCookie(self, handleRequestOutput, nameSuffix=''):
        header, body = handleRequestOutput.split(utils.CRLF*2,1)
        headerParts = header.split(utils.CRLF)
        sessionCookie = [p for p in headerParts[1:] if 'Set-Cookie' in p][0]
        cookieStartStr = 'Set-Cookie: session%s=' % nameSuffix
        self.assertTrue(sessionCookie.startswith(cookieStartStr), sessionCookie)

        sessionId = sessionCookie[len(cookieStartStr):sessionCookie.find(';')]
        return sessionId if sessionId else self.fail('Cookie-header has no value', sessionCookie)

    def testSessionUsesCurrentTimeForLastUsedTime(self):
        result = Session('asessionId, normally a hexdigest').lastUsedTime
        sleep(0.2)
        self.assertTrue(-0.001 < time() - result < 2.0)

    def testSessionComparesBasedOnLastUsedTime(self):
        sessions = []
        sessions.append(Session('3 sId'))
        sessions.append(Session('1 sId'))
        sessions.append(Session('2 sId'))
        sortedSessions = sessions[:]
        sortedSessions.sort()
        self.assertNotEqual(id(sessions), id(sortedSessions))
        self.assertEquals([sessions[0], sessions[1], sessions[2]], sortedSessions)

        s1 = Session('1 sId')
        s2 = Session('2 sId')
        s3 = Session('3 sId')
        pointInTime = time() - 3600
        s1.lastUsedTime = pointInTime
        s2.lastUsedTime = pointInTime + 1
        s3.lastUsedTime = pointInTime + 2
        sessions = []
        sessions.extend([s1, s2, s3])
        s1.lastUsedTime = pointInTime + 50
        s2.lastUsedTime = pointInTime + 25
        s3.lastUsedTime = pointInTime
        sortedSessions = sessions[:]
        sortedSessions.sort()
        self.assertEquals([sessions[2], sessions[1], sessions[0]], sortedSessions)

    def testDefaultSessionTimeout(self):
        TWO_HOURS = 3600 * 2
        sessions = []
        def handleRequest(session=None, *args, **kwargs):
            sessions.append(session)
            yield  utils.okHtml + '<html/>'
        self.observer.handleRequest = handleRequest

        result = ''.join(compose(self.handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345))))
        sessionIds = []
        sessionId = self.assertSessionCookie(result)
        sessionIds.append(sessionId)
        result = ''.join(compose(self.handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345))))
        sessionId = self.assertSessionCookie(result)
        sessionIds.append(sessionId)

        sessions[0].lastUsedTime = sessions[0].lastUsedTime - (TWO_HOURS + 1)
        result = ''.join(compose(self.handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345), Headers={'Cookie': 'session=%s' % sessions[0]['id']})))
        sessionId = self.assertSessionCookie(result)
        self.assertNotEqual(sessions[0]['id'], sessionId, "Timeout should have expired the Cookie: %s" % sessionId)

        result = ''.join(compose(self.handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345), Headers={'Cookie': 'session=%s' % sessions[1]['id']})))
        sessionId = self.assertSessionCookie(result)
        self.assertEquals(sessions[1]['id'], sessionId)
        self.assertTrue(-0.001 < time() - sessions[1].lastUsedTime < 2.0, "Time difference too big: %.1f seconds." % (time() - sessions[1].lastUsedTime))
        self.assertEquals(id(sessions[1]), id(sessions[3]))

    def testCustomSessionTimeout(self):
        HALF_AN_HOUR = 3600 / 2
        sessions = []
        def handleRequest(session=None, *args, **kwargs):
            sessions.append(session)
            yield  utils.okHtml + '<html/>'
        handler = SessionHandler(secretSeed='SessionHandlerTest', timeout=HALF_AN_HOUR)
        observer = CallTrace('Observer')
        observer.handleRequest = handleRequest
        handler.addObserver(observer)

        sessionIds = []
        for i in range(0, 4):
            result = ''.join(compose(handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345))))
            sessionId = self.assertSessionCookie(result)
            sessionIds.append(sessionId)

        sessions[0].lastUsedTime = sessions[0].lastUsedTime - (HALF_AN_HOUR + 3600)
        sessions[1].lastUsedTime = sessions[1].lastUsedTime - (HALF_AN_HOUR + 1)
        sessions[2].lastUsedTime = sessions[2].lastUsedTime - (HALF_AN_HOUR + 0)
        sessions[3].lastUsedTime = sessions[3].lastUsedTime - (HALF_AN_HOUR + -1)

        for i in range(0, 2):
            result = ''.join(compose(handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345), Headers={'Cookie': 'session=%s' % sessions[i]['id']})))
            sessionId = self.assertSessionCookie(result)
            self.assertNotEqual(sessions[i]['id'], sessionId, "Timeout should have expired the Cookie: %s, of session[%s]" % (sessionId, i))

        for i in range(3, 4):
            result = ''.join(compose(handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345), Headers={'Cookie': 'session=%s' % sessions[i]['id']})))
            sessionId = self.assertSessionCookie(result)
            self.assertEquals(sessions[i]['id'], sessionId)
            self.assertTrue(-0.001 < time() - sessions[i].lastUsedTime < 2.0, "Time difference too big: %.1f seconds." % (time() - sessions[i].lastUsedTime))

# Cookie bevat:
# - id (session)
# - time/date
# - expiration
# - IPAdress (Client)
# - MD5( bovenstaande + secret)

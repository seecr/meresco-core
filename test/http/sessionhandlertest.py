
from unittest import TestCase
from meresco.components.http import SessionHandler, utils
from meresco.framework import compose
from cq2utils import CallTrace

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
            yield session.setLink('linktitle', 'key', 'value')
        self.observer.handleRequest = handleRequest
        result = ''.join(compose(self.handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345), Headers={})))
        self.assertEquals('<a href="?key=%2Bvalue">linktitle</a>', result)
        

# Cookie bevat:
# - id (session)
# - time/date
# - expiration
# - IPAdress (Client)
# - MD5( bovenstaande + secret)
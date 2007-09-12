## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) 2007 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2007 Stichting Kennisnet Ict op school. 
#       http://www.kennisnetictopschool.nl
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
from random import randint
from weightless import Reactor, HttpReader, VERSION as WlVersion
from meresco.components.http import ObservableHttpServer, ObservableHttpServerAdapter
from cq2utils import CallTrace
from socket import gethostname
from cq2utils import MATCHALL

class ObservableHttpServerTest(TestCase):
    def testOne(self):
        port = randint(2**13, 2**16)
        reactor = Reactor()
        server = ObservableHttpServer(reactor, port)
        mockObserver = CallTrace()
        mockObserver.returnValues['handleRequest'] = (i for i in 'HTTP/1.0 200 Ok\r\n\r\nabc')
        server.addObserver(mockObserver)
        fragments = []
        def connect(*args, **kwargs):
            client.receiveFragment(response)
        def response(fragment):
            fragments.append(fragment)
        client = HttpReader(reactor, 'http://localhost:%d' % port, connect)
        while len(mockObserver.calledMethods) < 1:
            reactor.step()
        self.assertEquals('handleRequest', mockObserver.calledMethods[0].name)
        self.assertEquals({'port': port, 'RequestURI': '/', 'HTTPVersion': '1.0', 'Method': 'GET','Headers': {'Host': 'localhost', 'User-Agent': 'Weightless/v' + WlVersion}, 'Client': ('127.0.0.1', MATCHALL)}, mockObserver.calledMethods[0].kwargs)
        while len(fragments) < 3:
            reactor.step()
        self.assertEquals('abc', ''.join(fragments))

    def testOldStyleObservableServerAdapter(self):
        oldStyleComponent = CallTrace('oldStyleComponent')
        adapter = ObservableHttpServerAdapter()
        adapter.addObserver(oldStyleComponent)
        result = adapter.handleRequest(port=123, **{'RequestURI': '/?arg=1', 'HTTPVersion': '1.0', 'Method': 'GET','Headers': {'Host': 'somehost:12345', 'User-Agent': 'Weightless/v0.1'}, 'Client': ('127.0.0.1', 35623)})
        list(result)
        self.assertEquals('handleRequest', oldStyleComponent.calledMethods[0].name)
        webrequest = oldStyleComponent.calledMethods[0].args[0]
        self.assertEquals('/', webrequest.path)
        self.assertEquals('GET', webrequest.method)
        self.assertEquals('/?arg=1', webrequest.uri)
        self.assertEquals({'arg': ['1']}, webrequest.args)
        self.assertEquals({'Host': 'somehost:12345', 'User-Agent': 'Weightless/v0.1'}, webrequest.received_headers)
        self.assertEquals('127.0.0.1', webrequest.client.host)
        self.assertEquals('somehost', webrequest.getRequestHostname())
        self.assertEquals(123, webrequest.getHost().port)

    def testGetHostNameWithoutHostnameHeader(self):
        oldStyleComponent = CallTrace('oldStyleComponent')
        adapter = ObservableHttpServerAdapter()
        adapter.addObserver(oldStyleComponent)
        result = adapter.handleRequest(**{'RequestURI': '/?arg=1', 'HTTPVersion': '1.0', 'Method': 'GET','Headers': {'User-Agent': 'Weightless/v0.1'}, 'Client': ('127.0.0.1', 35623)})
        list(result)
        webrequest = oldStyleComponent.calledMethods[0].args[0]
        self.assertEquals(gethostname(), webrequest.getRequestHostname())

    def testWriteResponseWithAdapter(self):
        oldStyleComponent = CallTrace('oldStyleComponent')
        def handleRequest(webrequest):
            webrequest.write('ape')
        oldStyleComponent.handleRequest = handleRequest
        adapter = ObservableHttpServerAdapter()
        adapter.addObserver(oldStyleComponent)
        result = adapter.handleRequest(**{'RequestURI': '/?arg=1', 'HTTPVersion': '1.0', 'Method': 'GET','Headers': {'Host': 'localhost', 'User-Agent': 'Weightless/v0.1'}, 'Client': ('127.0.0.1', 35623)})
        self.assertEquals('HTTP/1.0 200 Ok\r\n\r\nape', ''.join(result))

    def testStr(self):
        oldStyleComponent = CallTrace('oldStyleComponent')
        adapter = ObservableHttpServerAdapter()
        adapter.addObserver(oldStyleComponent)
        result = adapter.handleRequest(**{'RequestURI': '/?arg=1', 'HTTPVersion': '1.0', 'Method': 'GET','Headers': {'User-Agent': 'Weightless/v0.1'}, 'Client': ('127.0.0.1', 35623)})
        list(result)
        webrequest = oldStyleComponent.calledMethods[0].args[0]
        self.assertEquals('127.0.0.1\tGET\t/?arg=1', str(webrequest))

    def testSetResponseCodeAndHeader(self):
        oldStyleComponent = CallTrace('oldStyleComponent')
        def handleRequest(webrequest):
            webrequest.setHeader('content-type', 'text/xml')
            webrequest.setResponseCode(302)
        oldStyleComponent.handleRequest = handleRequest
        adapter = ObservableHttpServerAdapter()
        adapter.addObserver(oldStyleComponent)
        result = adapter.handleRequest(**{'RequestURI': '/?arg=1', 'HTTPVersion': '1.0', 'Method': 'GET','Headers': {'Host': 'localhost', 'User-Agent': 'Weightless/v0.1'}, 'Client': ('127.0.0.1', 35623)})
        self.assertEquals('HTTP/1.0 302 Ok\r\nContent-Type: text/xml\r\n\r\n', ''.join(result))

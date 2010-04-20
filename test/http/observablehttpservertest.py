## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2010 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2010 Stichting Kennisnet http://www.kennisnet.nl
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
from socket import socket
from cq2utils import CQ2TestCase, CallTrace
from weightless import Reactor

from meresco.components.http import ObservableHttpServer
from meresco.components.http.utils import CRLF

class ObservableHttpServerTest(CQ2TestCase):
    def testSimpleHandleRequest(self):
        observer = CallTrace('Observer')
        s = ObservableHttpServer(CallTrace('Reactor'), 1024)
        s.addObserver(observer)

        list(s.handleRequest(RequestURI='http://localhost'))
        self.assertEquals(1, len(observer.calledMethods))
        method = observer.calledMethods[0]
        self.assertEquals('handleRequest', method.name)
        self.assertEquals(0, len(method.args))
        self.assertEquals(7, len(method.kwargs))

    def testHandleRequest(self):
        observer = CallTrace('Observer')
        s = ObservableHttpServer(CallTrace('Reactor'), 1024)
        s.addObserver(observer)

        list(s.handleRequest(RequestURI='http://localhost/path?key=value&emptykey#fragment'))
        self.assertEquals(1, len(observer.calledMethods))
        method = observer.calledMethods[0]
        self.assertEquals('handleRequest', method.name)
        self.assertEquals(0, len(method.args))
        self.assertEquals(7, len(method.kwargs))
        self.assertTrue('arguments' in method.kwargs, method.kwargs)
        arguments = method.kwargs['arguments']
        self.assertEquals(2, len(arguments))
        self.assertEquals(['emptykey', 'key'], sorted(arguments.keys()))
        self.assertEquals(['value'], arguments['key'])
        self.assertEquals([''], arguments['emptykey'])

    def testMaxConnectionsErrorHandling(self):
        observer = CallTrace('Observer')
        reactor = CallTrace('Reactor')

        s = ObservableHttpServer(reactor, 1024, maxConnections=5)
        s.addObserver(observer)
        result = ''.join(s._error(ResponseCode=503, something='bicycle'))

        self.assertEquals(1, len(observer.calledMethods))
        self.assertEquals('logHttpError', observer.calledMethods[0].name)
        self.assertEquals({'ResponseCode': 503, 'something': 'bicycle'}, observer.calledMethods[0].kwargs)
        header, body = result.split(CRLF * 2)
        self.assertTrue(header.startswith('HTTP/1.0 503'), header)
        self.assertTrue('Service Unavailable' in body, body)

    def testErrorHandlerRegisteredOnWeightlessHttpServer(self):
        reactor = CallTrace('Reactor')

        s = ObservableHttpServer(reactor, 1024, maxConnections=5)
        s.startServer()

        acceptor = s._keepHttpServerForTestingSupport
        httphandler = acceptor._sinkFactory('sok')
        errorHandler = httphandler._errorHandler
        self.assertTrue(errorHandler == s._error)

    def testServerWithPrio(self):
        import gc, weakref
        prios = []
        class MyServer(object):
            def handleRequest(self, *args, **kwargs):
                yield 'HALLO'
        class MyReactor(Reactor):
            def addReader(self, *args, **kwargs):
                prios.append(('read', kwargs['prio']))
                return Reactor.addReader(self, *args, **kwargs)
            def addWriter(self, *args, **kwargs):
                prios.append(('write', kwargs['prio']))
                return Reactor.addWriter(self, *args, **kwargs)
        reactor = MyReactor()
        s = ObservableHttpServer(reactor, 2000, prio=3)
        s.addObserver(MyServer())
        s.observer_init()
        sok = socket()
        sok.connect(('localhost', 2000))
        sok.send('GET / HTTP/1.0\r\n\r\n')
        reactor.step()
        self.assertEquals([('read', 3)], prios)
        reactor.step().step()
        self.assertEquals([('read', 3), ('read', 3)], prios)
        reactor.step()
        reactor.step()
        self.assertEquals([('read', 3), ('read', 3), ('write', 3)], prios)
        # one more step to let the connection finalize and all objects reclaimed and avoid garbage
        reactor.step()
        gc.collect()
        garbage = [weakref.ref(o) for o in gc.get_objects() if 'AllMess' in str(type(o))]
        self.assertEquals([], garbage)


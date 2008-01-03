## begin license ##
#
#    Meresco Core is an open-source library containing components to build 
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school. 
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
from random import randint
from weightless import Reactor, HttpReader, VERSION as WlVersion
from weightless._httpreader import HttpReaderFacade
from meresco.components.http import ObservableHttpServer
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
        def send(data):
            if type(data) == str:
                fragments.append(data)
        client = HttpReaderFacade(reactor, 'http://localhost:%d' % port, send)
        while len(mockObserver.calledMethods) < 1:
            reactor.step()
        self.assertEquals('handleRequest', mockObserver.calledMethods[0].name)
        self.assertEquals({'Body': '', 'port': port, 'RequestURI': '/', 'HTTPVersion': '1.1', 'Method': 'GET','Headers': {'Host': 'localhost', 'User-Agent': 'Weightless/v' + WlVersion}, 'Client': ('127.0.0.1', MATCHALL)}, mockObserver.calledMethods[0].kwargs)
        while len(fragments) < 3:
            reactor.step()
        self.assertEquals('abc', ''.join(fragments))

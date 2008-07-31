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


from cq2utils import CQ2TestCase, CallTrace
from meresco.framework import Observable, be
from cStringIO import StringIO

from meresco.components.oai import OaiMain

class OaiMainTest(CQ2TestCase):

    def setUp(self):
        CQ2TestCase.setUp(self)
        self.subject = self.getSubject()
        self.subject.getTime = lambda : '2007-02-07T00:00:00Z'
        self.observable = be(
            (Observable(),
                (self.subject, )
            )
        )
        self.request = CallTrace('Request')
        self.request.path = '/path/to/oai'
        self.request.getRequestHostname = lambda: 'server'
        class Host:
            def __init__(self):
                self.port = '9000'
        self.request.getHost = lambda: Host()
        self.stream = StringIO()
        self.request.write = self.stream.write

    def getSubject(self):
        return OaiMain()

    def testCallsUnknown(self):
        observer = Observer()
        self.subject.addObserver(observer)
        self.request.args = {'verb': ['SomeVerb']}

        self.observable.do.handleRequest(self.request)

        self.assertEquals('someVerb', observer.message)
        self.assertEquals(1, len(observer.args))
        self.assertTrue(self.request is observer.args[0])

    def testCallsUnknownWhenNoVerb(self):
        observer = Observer()
        self.subject.addObserver(observer)
        self.request.args = {}

        self.observable.do.handleRequest(self.request)

        self.assertEquals('', observer.message)
        self.assertEquals(1, len(observer.args))
        self.assertTrue(self.request is observer.args[0])

    def testCallFirstThingOnly(self):
        observer1 = Observer()
        observer2 = Observer()
        be(
            (self.subject,
                (observer1,),
                (observer2,)
            )
        )
        self.request.args = {'verb': ['SomeVerb']}
        usedargs=[]
        def someVerb(webrequest):
            usedargs.append(webrequest)
        observer1.someVerb = someVerb

        self.observable.do.handleRequest(self.request)

        self.assertEquals(1, len(usedargs))
        self.assertEquals(None, observer2.message)


class Observer(object):
    def __init__(self):
        self.message = None
        self.args = None
    def unknown(self, message, *args):
        self.message = message
        self.args = args
        yield None

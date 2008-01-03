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

from cStringIO import StringIO

from cq2utils.cq2testcase import CQ2TestCase
from cq2utils.calltrace import CallTrace

from amara import binderytools

from meresco.components.venturi import Venturi

class VenturiTest(CQ2TestCase):
    def setUp(self):
        CQ2TestCase.setUp(self)
        self.storage = CallTrace('Storage')
        self.unit = CallTrace('Unit')
        self.storage.returnValues['getUnit'] = self.unit
        self.venturi = Venturi('venturiName', self.storage)
        self.observer = CallTrace('Observer')
        self.venturi.addObserver(self.observer)

    def testWithNonExistingVenturiObject(self):
        meta = binderytools.bind_string('<meta><tagOne>data</tagOne></meta>').meta
        list(self.venturi.add('id', 'meta', meta))
        self.assertEquals(['getUnit'], [method.name for method in self.storage.calledMethods])
        self.assertEquals(['hasBox'], [method.name for method in self.unit.calledMethods])

        self.assertEquals(1, len(self.observer.calledMethods))
        method = self.observer.calledMethods[0]
        self.assertEquals('add', method.name)
        self.assertEquals(3, len(method.arguments))
        self.assertEquals('id', method.arguments[0])
        self.assertEquals('venturiName', method.arguments[1])
        self.assertEqualsWS("""<venturiName>
    <meta>
        <tagOne>data</tagOne>
    </meta>
</venturiName>""", method.arguments[2].xml())

    def testWithExistingVenturiObjectWithoutMeta(self):
        meta = binderytools.bind_string('<meta><tagOne>data</tagOne></meta>').meta
        self.unit.returnValues['hasBox'] = True
        self.unit.returnValues['openBox'] = StringIO("""<venturiName>
    <lom>
        <general><title>data</title></general>
    </lom>
</venturiName>""")

        list(self.venturi.add(id, 'meta', meta))

        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEqualsWS("""<venturiName>
    <lom>
        <general><title>data</title></general>
    </lom>
    <meta>
        <tagOne>data</tagOne>
    </meta>
</venturiName>""", self.observer.calledMethods[0].arguments[2].xml())

    def testWithExistingVenturiObjectWithMeta(self):
        meta = binderytools.bind_string('<meta><tagOne>data</tagOne></meta>').meta
        self.unit.returnValues['hasBox'] = True
        self.unit.returnValues['openBox'] = StringIO("""<venturiName>
    <meta>
        <already>here</already>
    </meta>
</venturiName>""")
        list(self.venturi.add('id', 'meta', meta))
        self.assertEquals(1, len(self.observer.calledMethods))
        args = self.observer.calledMethods[0].arguments
        self.assertEqualsWS("""<venturiName>
    <meta>
        <tagOne>data</tagOne>
    </meta>
</venturiName>""", args[2].xml())


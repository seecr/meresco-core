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

from StringIO import StringIO

from cq2utils import CQ2TestCase, CallTrace
from lxml.etree import fromstring, tostring

from meresco.components.venturi import Venturi
from weightless import compose

class VenturiTest(CQ2TestCase):
    def testOutline(self):
        inputEvent = fromstring("""<document><part name="partone">&lt;some&gt;message&lt;/some&gt;</part><part name="parttwo"><second>message</second></part></document>""")
        interceptor = CallTrace('Interceptor')
        v = Venturi(
            should=[('partone', '/document/part[@name="partone"]/text()'),
                    ('parttwo', '/document/part/second')],
            namespaceMap={})
        v.addObserver(interceptor)
        list(compose(v.add('identifier', 'document', inputEvent)))
        self.assertEquals(['add', 'add', 'finish'], [m.name for m in interceptor.calledMethods])
        self.assertEquals(('identifier', 'partone'), interceptor.calledMethods[0].args[:2])
        self.assertEquals('<some>message</some>', tostring(interceptor.calledMethods[0].args[2]))
        self.assertEquals(('identifier', 'parttwo',), interceptor.calledMethods[1].args[:2])
        secondXml = interceptor.calledMethods[1].args[2]
        self.assertEquals('<second>message</second>', tostring(secondXml))
        self.assertEquals('second', secondXml.getroot().tag)
        

    def testOnlyPassPartsSpecified(self):
        inputEvent = fromstring("""<document><part name="partone">&lt;some&gt;message&lt;/some&gt;</part><part name="parttwo"><second/></part></document>""")
        interceptor = CallTrace('Interceptor')
        v = Venturi(
            should=[('partone', '/document/part[@name="partone"]/text()')],
            namespaceMap={})
        v.addObserver(interceptor)
        list(compose(v.add('identifier', 'document', inputEvent)))
        self.assertEquals(['add', 'finish'], [m.name for m in interceptor.calledMethods])
        self.assertEquals('<some>message</some>', tostring(interceptor.calledMethods[0].args[2]))

    def testReadFromStorage(self):
        inputEvent = fromstring('<document/>')
        interceptor = CallTrace('Interceptor', ignoredAttributes=['getStream', 'unknown'])
        storage = CallTrace('Storage', ignoredAttributes=['add', 'finish'])
        storage.returnValues['getStream'] = StringIO('<some>message</some>')
        v = Venturi(
            should=[('partone', '/document/part[@name="partone"]/text()')],
            namespaceMap={})
        v.addObserver(interceptor)
        v.addObserver(storage)
        list(compose(v.add('identifier', 'document', inputEvent)))
        self.assertEquals(['add', 'finish'], [m.name for m in interceptor.calledMethods])
        self.assertEquals('<some>message</some>', tostring(interceptor.calledMethods[0].args[2]))
        self.assertEquals(('identifier', 'partone'), storage.calledMethods[0].args)

    def testCouldHave(self):
        inputEvent = fromstring('<document><one/></document>')
        interceptor = CallTrace('Interceptor', ignoredAttributes=['getStream', 'unknown'])
        v = Venturi(
            could=[('one', '/document/one')],
            namespaceMap={})
        v.addObserver(interceptor)
        list(compose(v.add('identifier', 'document', inputEvent)))
        self.assertEquals(['add', 'finish'], [m.name for m in interceptor.calledMethods])
        self.assertEquals('<one/>', tostring(interceptor.calledMethods[0].args[2]))
    
    def testCouldHaveInStorage(self):
        inputEvent = fromstring('<document><other/></document>')
        interceptor = CallTrace('Interceptor', ignoredAttributes=['getStream', 'unknown'])
        storage = CallTrace('Storage', ignoredAttributes=['add', 'finish'])
        storage.returnValues['getStream'] = StringIO('<one/>')
        v = Venturi(
            could=[('one', '/document/one')],
            namespaceMap={})
        v.addObserver(interceptor)
        v.addObserver(storage)
        list(compose(v.add('identifier', 'document', inputEvent)))
        self.assertEquals(['add', 'finish'], [m.name for m in interceptor.calledMethods])
        self.assertEquals('<one/>', tostring(interceptor.calledMethods[0].args[2]))
        self.assertEquals(('identifier', 'one'), storage.calledMethods[0].args)

    def testCouldHaveButDoesnot(self):
        inputEvent = fromstring('<document><other/></document>')
        interceptor = CallTrace('Interceptor', ignoredAttributes=['getStream', 'unknown'])
        storage = CallTrace('Storage', ignoredAttributes=['add', 'finish'])
        storage.exceptions['getStream'] = MyException('Not Available')
        v = Venturi(
            should=[('other', '/document/other')],
            could=[('one', '/document/one')],
            namespaceMap={})
        v.addObserver(interceptor)
        v.addObserver(storage)
        list(compose(v.add('identifier', 'document', inputEvent)))
        self.assertEquals(['add', 'finish'], [m.name for m in interceptor.calledMethods])
        self.assertEquals(('identifier', 'other',), interceptor.calledMethods[0].args[:2])

    def testXpathReturnsMultipleResults(self):
        inputEvent = fromstring('<document><one/><two/></document>')
        v = Venturi(
            should=[('one', '/document/*')],
            namespaceMap={})
        try:
            list(compose(v.add('identifier', 'document', inputEvent)))
            self.fail()
        except Exception, e:
            self.assertEquals("XPath '/document/*' should return atmost one result.", str(e))

    def testNamespace(self):
        inputEvent = fromstring('<document xmlns="ns1" xmlns:ns2="ns2"><ns2:one/><two/></document>')
        interceptor = CallTrace('Interceptor')
        v = Venturi(
            should=[('one', '/prefixone:document/prefixtwo:one'),
                    ('two', '/prefixone:document/prefixone:two')],
            namespaceMap={'prefixone':'ns1', 'prefixtwo':'ns2'})
        v.addObserver(interceptor)
        list(compose(v.add('identifier', 'document', inputEvent)))
        self.assertEquals(['add', 'add', 'finish'], [m.name for m in interceptor.calledMethods])
        

class MyException(Exception):
    pass

## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
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

from StringIO import StringIO

from cq2utils import CQ2TestCase, CallTrace
from lxml.etree import parse, tostring

from meresco.components.venturi import Venturi, VenturiException
from meresco.core import TransactionScope, be, Observable
from weightless import compose


def fromstring(aString):
    xmlParsed = parse(StringIO(aString))
    return xmlParsed

def createVenturiHelix(should, could, *observers, **kwargs):
    return be(
        (Observable(),
            (TransactionScope('document'),
                (Venturi(
                        should=should,
                        could=could,
                        namespaceMap=kwargs.get('namespaceMap', {})),)
                    +tuple((observer,) for observer in observers)
            )
        )
    )

class VenturiTest(CQ2TestCase):
    def testOutline(self):
        inputEvent = fromstring("""<document><part name="partone">&lt;some&gt;message&lt;/some&gt;</part><part name="parttwo"><second>message</second></part></document>""")
        interceptor = CallTrace('Interceptor')
        v = createVenturiHelix([('partone', '/document/part[@name="partone"]/text()'), ('parttwo', '/document/part/second')], [], interceptor)
        list(v.all.add('identifier', 'document', inputEvent))
        self.assertEquals(['begin', 'add', 'add'], [m.name for m in interceptor.calledMethods])
        self.assertEquals(('identifier', 'partone'), interceptor.calledMethods[1].args[:2])
        self.assertEquals('<some>message</some>', tostring(interceptor.calledMethods[1].args[2]))
        self.assertEquals(('identifier', 'parttwo',), interceptor.calledMethods[2].args[:2])
        secondXml = interceptor.calledMethods[2].args[2]
        self.assertEquals('<second>message</second>', tostring(secondXml))
        self.assertEquals('second', secondXml.getroot().tag)


    def testOnlyPassPartsSpecified(self):
        inputEvent = fromstring("""<document><part name="partone">&lt;some&gt;message&lt;/some&gt;</part><part name="parttwo"><second/></part></document>""")
        interceptor = CallTrace('Interceptor')
        v = createVenturiHelix([('partone', '/document/part[@name="partone"]/text()')], [], interceptor)
        list(v.all.add('identifier', 'document', inputEvent))
        self.assertEquals(['begin', 'add'], [m.name for m in interceptor.calledMethods])
        self.assertEquals('<some>message</some>', tostring(interceptor.calledMethods[1].args[2]))

    def testReadFromStorage(self):
        inputEvent = fromstring('<document/>')
        interceptor = CallTrace('Interceptor', ignoredAttributes=['isAvailable', 'getStream', 'unknown'])
        storage = CallTrace('Storage', ignoredAttributes=['add'])
        storage.returnValues['isAvailable'] = (True, True)
        storage.returnValues['getStream'] = StringIO('<some>this is partone</some>')
        v = createVenturiHelix([('partone', '/document/part[@name="partone"]/text()')], [], interceptor, storage)
        v.do.add('identifier', 'document', inputEvent)
        self.assertEquals(['begin', 'add'], [m.name for m in interceptor.calledMethods])
        self.assertEquals('<some>this is partone</some>', tostring(interceptor.calledMethods[1].args[2]))
        self.assertEquals(('identifier', 'partone'), storage.calledMethods[1].args)

    def testCouldHave(self):
        inputEvent = fromstring('<document><one/></document>')
        interceptor = CallTrace('Interceptor', ignoredAttributes=['getStream', 'unknown'])
        v = createVenturiHelix([], [('one', '/document/one')], interceptor)
        list(v.all.add('identifier', 'document', inputEvent))
        self.assertEquals(['begin', 'add'], [m.name for m in interceptor.calledMethods])
        self.assertEquals('<one/>', tostring(interceptor.calledMethods[1].args[2]))

    def testCouldHaveInStorage(self):
        inputEvent = fromstring('<document><other/></document>')
        interceptor = CallTrace('Interceptor', ignoredAttributes=['isAvailable', 'getStream', 'unknown'])
        storage = CallTrace('Storage', ignoredAttributes=['add'])
        storage.returnValues['isAvailable'] = (True, True)
        storage.returnValues['getStream'] = StringIO('<one/>')
        v = createVenturiHelix([], [('one', '/document/one')], interceptor, storage)
        list(v.all.add('identifier', 'document', inputEvent))
        self.assertEquals(['begin', 'add'], [m.name for m in interceptor.calledMethods])
        self.assertEquals('<one/>', tostring(interceptor.calledMethods[1].args[2]))
        self.assertEquals(('identifier', 'one'), storage.calledMethods[1].args)

    def testCouldHaveButDoesnot(self):
        inputEvent = fromstring('<document><other/></document>')
        interceptor = CallTrace('Interceptor', ignoredAttributes=['isAvailable', 'getStream', 'unknown'])
        storage = CallTrace('Storage', ignoredAttributes=['add'])
        storage.exceptions['getStream'] = KeyError('Part not available')
        v = createVenturiHelix([('other', '/document/other')], [('one', '/document/one')], interceptor, storage)
        list(v.all.add('identifier', 'document', inputEvent))
        self.assertEquals(['begin', 'add'], [m.name for m in interceptor.calledMethods])
        self.assertEquals(('identifier', 'other',), interceptor.calledMethods[1].args[:2])

    def testXpathReturnsMultipleResults(self):
        inputEvent = fromstring('<document><one/><two/></document>')
        v = createVenturiHelix([('one', '/document/*')], [])
        try:
            result = v.all.add('identifier', 'document', inputEvent)
            list(result)
            self.fail('no good no')
        except Exception, e:
            self.assertEquals("XPath '/document/*' should return atmost one result.", str(e))
        finally:
            result.close()

    def testNamespace(self):
        inputEvent = fromstring('<document xmlns="ns1" xmlns:ns2="ns2"><ns2:one/><two/></document>')
        interceptor = CallTrace('Interceptor')
        v = createVenturiHelix([('one', '/prefixone:document/prefixtwo:one'), ('two','/prefixone:document/prefixone:two')], [], interceptor, namespaceMap={'prefixone':'ns1', 'prefixtwo':'ns2'})
        list(v.all.add('identifier', 'document', inputEvent))
        self.assertEquals(['begin', 'add', 'add'], [m.name for m in interceptor.calledMethods])

    def testTransactionScopeFilledWithIdentifier(self):
        ids = []
        class TempComponent(Observable):
            def add(this, oldStyleId, partname, data):
                ids.append(this.ctx.tx.locals['id'])
        v = createVenturiHelix([('PARTNAME', '/document')],[], TempComponent())
        v.do.add('ID', 'PARTNAME', fromstring('<document><other/></document>'))
        self.assertEquals(1, len(ids))

    def testDeleteAlsoSetsIdOnTransaction(self):
        __callstack_var_tx__ = CallTrace('Transaction')
        __callstack_var_tx__.locals={}
        v = Venturi(should=[('PARTNAME', '/document')],could=[])
        v.delete('identifier')
        self.assertEquals('identifier', __callstack_var_tx__.locals['id'])

    def testPartInShouldDoesNotExist(self):
        inputEvent = fromstring('<document/>')
        interceptor = CallTrace('Interceptor', ignoredAttributes=['begin', 'isAvailable', 'getStream', 'unknown'])
        storage = CallTrace('Storage', ignoredAttributes=['begin', 'add'])
        storage.returnValues['isAvailable'] = (False, False)
        v = createVenturiHelix([('partone', '/document/part[@name="partone"]/text()')], [], interceptor, storage)
        try:
            v.do.add('identifier', 'document', inputEvent)
            self.fail('Expected exception')
        except VenturiException:
            pass
        self.assertEquals([], [m.name for m in interceptor.calledMethods])
        self.assertEquals(['isAvailable'], [m.name for m in storage.calledMethods])

    def testAddDocumentPartCallsAdd(self):
        v = Venturi()
        addInvocations = []
        def add(*args, **kwargs):
            addInvocations.append(dict(args=args, kwargs=kwargs))
        v.add = add
        v.addDocumentPart(identifier='x', name='y', lxmlNode='dummy')
        self.assertEquals([{'args':(), 'kwargs':dict(identifier='x', name='y', lxmlNode='dummy')}], addInvocations)


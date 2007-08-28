## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) SURF Foundation. http://www.surf.nl
#    Copyright (C) Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) SURFnet. http://www.surfnet.nl
#    Copyright (C) Stichting Kennisnet Ict op school.
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
from time import strftime, gmtime
from cq2utils.cq2testcase import CQ2TestCase
from cq2utils.calltrace import CallTrace

from os.path import join
from PyLucene import BooleanQuery
from storage import Storage
from amara import binderytools
from amara.binderytools import bind_string

from meresco.components.oai import OaiJazzLucene
from meresco.components.xml2document import TEDDY_NS, Xml2Document
from meresco.framework.observable import Observable
from meresco.components.lucene.document import Document
from meresco.components.lucene.lucene import LuceneIndex
from meresco.components import StorageComponent


FIELDS = binderytools.bind_string("""<xmlfields xmlns:teddy="%s">
    <field1>this is field1</field1>
    <untokenizedField teddy:tokenize="false">this should not be tokenized</untokenizedField>
</xmlfields>""" % TEDDY_NS).xmlfields

class OaiJazzLuceneTest(CQ2TestCase):
    def setUp(self):
        CQ2TestCase.setUp(self)
        self.index = CallTrace("Index")
        self.storage = CallTrace("Storage")
        self.mockedjazz = OaiJazzLucene(self.index, self.storage, (i for i in xrange(100)))
        self.id = "id"
        self.partName = "xmlfields"
        self.document = Xml2Document()._create(self.id, FIELDS)
        self.realjazz = OaiJazzLucene(LuceneIndex(join(self.tempdir,'index')),
            StorageComponent(join(self.tempdir,'storage')), iter(xrange(99)))


    def testAdd(self):
        self.mockedjazz.add(self.id, self.partName, bind_string('<empty/>'))
        self.assertEquals(2,len(self.index.calledMethods))
        self.assertEquals("deleteID('id')", str(self.index.calledMethods[0]))
        self.assertEquals('addToIndex(<meresco.components.lucene.document.Document>)', str(self.index.calledMethods[1]))

    def testDelete(self):
        self.mockedjazz.delete(self.id)
        self.assertEquals(1,len(self.index.calledMethods))
        self.assertEquals("deleteID('id')", str(self.index.calledMethods[0]))

    def testListRecords(self):
        self.mockedjazz.oaiSelect(None, 'PART', '0', None, None)
        executeQueryMethod = self.index.calledMethods[0]
        self.assertEquals(2, len(executeQueryMethod.arguments))
        self.assertEquals('+oaimeta.prefixes.prefix:PART', str(executeQueryMethod.arguments[0]))
        self.assertEquals('oaimeta.unique', executeQueryMethod.arguments[1])

    def testListRecordsParams(self):
        self.mockedjazz.oaiSelect('ONE:TWO:THREE', 'PART', '0010', '2000-01-01T00:00:00Z', '2000-31-12T00:00:00Z')
        executeQueryMethod = self.index.calledMethods[0]
        queryWrapper = executeQueryMethod.arguments[0]
        self.assertEquals(2, len(executeQueryMethod.arguments))
        self.assertEquals('+oaimeta.prefixes.prefix:PART +oaimeta.unique:{0010 TO *] +oaimeta.datestamp:[2000-01-01T00:00:00Z TO 2000-31-12T00:00:00Z] +oaimeta.sets.setSpec:ONE:TWO:THREE', str(executeQueryMethod.arguments[0]))
        self.assertEquals('oaimeta.unique', executeQueryMethod.arguments[1])

    def testGetUnique(self):
        def getStream(id, partName):
            yield """<oaimeta>
        <stamp>DATESTAMP_FOR_TEST</stamp>
        <unique>UNIQUE_FOR_TEST</unique>
		<sets/>
		<prefixes/>
    </oaimeta>"""
        self.storage.getStream = getStream
        uniqueNumber = self.mockedjazz.getUnique('somedocid')
        self.assertEquals('UNIQUE_FOR_TEST', uniqueNumber)

    def testAddPartWithUniqueNumbersAndSorting(self):
        jazz = self.realjazz
        jazz.add('123', 'oai_dc', bind_string('<empty/>'), bind_string('<oai_dc/>'))
        jazz.add('124', 'lom', bind_string('<empty/>'), bind_string('<lom/>'))
        jazz.add('121', 'lom', bind_string('<empty/>'), bind_string('<lom/>'))
        jazz.add('122', 'lom', bind_string('<empty/>'), bind_string('<lom/>'))
        results =jazz.oaiSelect(None, 'oai_dc', '0', None, None)
        self.assertEquals(1, len(results))
        results =jazz.oaiSelect(None, 'lom', '0', None, None)
        self.assertEquals(3, len(results))
        self.assertEquals('124', results[0])
        self.assertEquals('121', results[1])
        self.assertEquals('122', results[2])

    def testAddSetInfo(self):
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>%s</setSpec></header>'
        jazz = self.realjazz
        jazz.add('123', 'oai_dc', bind_string('<empty/>'), bind_string(header % 1))
        jazz.add('124', 'oai_dc', bind_string('<empty/>'), bind_string(header % 2))
        results =jazz.oaiSelect('1', 'oai_dc', '0', None, None)
        self.assertEquals(1, len(results))
        results =jazz.oaiSelect('2', 'oai_dc', '0', None, None)
        self.assertEquals(1, len(results))
        results =jazz.oaiSelect(None, 'oai_dc', '0', None, None)
        self.assertEquals(2, len(results))

    def testAddRecognizeNamespace(self):
        header = '<header xmlns="this.is.not.the.right.ns"><setSpec>%s</setSpec></header>'
        jazz = self.realjazz
        jazz.add('123', 'oai_dc', bind_string('<empty/>'), bind_string(header % 1))
        results =jazz.oaiSelect('1', 'oai_dc', '0', None, None)
        self.assertEquals(0, len(results))
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>%s</setSpec></header>'
        jazz.add('124', 'oai_dc', bind_string('<empty/>'), bind_string(header % 1))
        results =jazz.oaiSelect('1', 'oai_dc', '0', None, None)
        self.assertEquals(1, len(results))

    def testMultipleHierarchicalSets(self):
        spec = "<setSpec>%s</setSpec>"
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/">%s</header>'
        jazz = self.realjazz
        jazz.add('124', 'oai_dc', bind_string('<empty/>'), bind_string(header % (spec % '2:3' + spec % '3:4')))
        self.assertEquals(1, len(jazz.oaiSelect('2', 'oai_dc', '0', None, None)))
        self.assertEquals(1, len(jazz.oaiSelect('2:3', 'oai_dc', '0', None, None)))
        self.assertEquals(1, len(jazz.oaiSelect('3', 'oai_dc', '0', None, None)))
        self.assertEquals(1, len(jazz.oaiSelect('3:4', 'oai_dc', '0', None, None)))

    def testGetSets(self):
        jazz = self.realjazz
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>%s</setSpec></header>'
        jazz.add('124', 'oai_dc', bind_string('<empty/>'), bind_string(header % 1))
        sets = jazz.getSets('124')
        self.assertEquals(['1'], sets)
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>%s</setSpec></header>'
        jazz.add('125', 'oai_dc', bind_string('<empty/>'), bind_string(header % 2))
        sets = jazz.getSets('125')
        self.assertEquals(['2'], sets)
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>1:2</setSpec><setSpec>2</setSpec></header>'
        jazz.add('124', 'oai_dc', bind_string('<empty/>'), bind_string(header))
        sets = jazz.getSets('124')
        self.assertEquals(['1', '1:2', '2'], sets)

    def testSetSpecWithTokensSplit(self):
        jazz = self.realjazz
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>%s</setSpec></header>'
        jazz.add('124', 'oai_dc', bind_string('<empty/>'), bind_string(header % "1:23"))
        results = jazz.oaiSelect('1:23', 'oai_dc', '0', None, None)
        self.assertEquals(1, len(results))

    def testDelete(self):
        jazz = self.realjazz
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>%s</setSpec></header>'
        jazz.add('123', 'oai_dc', bind_string('<empty/>'), bind_string(header % "1"))
        self.assertFalse(jazz.isDeleted('123'))
        self.assertEquals(1, len(jazz.oaiSelect(None, 'oai_dc', '0', None, None)))
        jazz.delete('123')
        self.assertTrue(jazz.isDeleted('123'))
        self.assertEquals(1, len(jazz.oaiSelect(None, 'oai_dc', '0', None, None)))

    def testDeleteAndReAdd(self):
        jazz = self.realjazz
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>%s</setSpec></header>'
        jazz.add('123', 'oai_dc', bind_string('<empty/>'), bind_string(header % "1"))
        jazz.delete('123')
        jazz.add('123', 'oai_dc', bind_string('<empty/>'), bind_string(header % "1"))
        self.assertFalse(jazz.isDeleted('123'))

    def testGetParts(self):
        jazz = self.realjazz
        jazz.add('123', 'oai_dc', bind_string('<empty/>'), bind_string('<dc/>').dc)
        jazz.add('123', 'lom', bind_string('<empty/>'), bind_string('<lom/>').lom)
        parts = jazz.getParts('123')
        self.assertEquals(['oai_dc', 'lom'], parts)
        self.assertEquals(['123'], list(jazz.oaiSelect(None, 'lom', '0', None, None)))
        self.assertEquals(['123'], list(jazz.oaiSelect(None, 'oai_dc', '0', None, None)))

    def testAddDocsWithSets(self):
        jazz = self.realjazz
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>%s</setSpec></header>'
        jazz.add('456', 'oai_dc', bind_string('<empty/>'), bind_string(header % 'set1'))
        jazz.add('457', 'oai_dc', bind_string('<empty/>'), bind_string(header % 'set2'))
        jazz.add('458', 'oai_dc', bind_string('<empty/>'), bind_string(header % 'set3'))
        sets = jazz.listSets()
        self.assertEquals(['set1', 'set2', 'set3'], sets)

    def testHierarchicalSets(self):
        jazz = self.realjazz
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>%s</setSpec></header>'
        jazz.add('456', 'oai_dc', bind_string('<empty/>'), bind_string(header % 'set1:set2:set3'))
        sets = jazz.listSets()
        self.assertEquals(['set1', 'set1:set2', 'set1:set2:set3'], sorted(sets))

    def testDatestamp(self):
        jazz = self.realjazz
        lower = strftime('%Y-%m-%dT%H:%M:%SZ', gmtime())
        jazz.add('456', 'oai_dc', bind_string('<empty/>'), bind_string('<data/>'))
        upper = strftime('%Y-%m-%dT%H:%M:%SZ', gmtime())
        datestamp = jazz.getDatestamp('456')
        self.assertTrue(lower <= datestamp <= upper, datestamp)

    def testMetadataPrefixes(self):
        jazz = self.realjazz
        jazz.add('456', 'oai_dc', bind_string('<oai_dc:dc xmlns:oai_dc="http://oai_dc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
             xsi:schemaLocation="http://oai_dc http://oai_dc/dc.xsd"/>'))
        prefixes = jazz.getAllPrefixes()
        self.assertEquals([('oai_dc', 'http://oai_dc/dc.xsd', 'http://oai_dc')], list(prefixes))
        jazz.add('457', 'dc2', bind_string('<oai_dc:dc xmlns:oai_dc="http://dc2"/>'))
        prefixes = jazz.getAllPrefixes()
        self.assertEquals(set([('oai_dc', 'http://oai_dc/dc.xsd', 'http://oai_dc'), ('dc2', '', 'http://dc2')]), prefixes)

    def testIncompletePrefixInfo(self):
        jazz = self.realjazz
        jazz.add('457', 'dc2', bind_string('<oai_dc/>'))
        prefixes = jazz.getAllPrefixes()
        self.assertEquals(set([('dc2', '', '')]), prefixes)

class OaiJazzLuceneIntegrationTest(CQ2TestCase):
    def setUp(self):
        CQ2TestCase.setUp(self)
        self._luceneIndex = LuceneIndex(join(self.tempdir, "lucene-index"))
        self._storage = StorageComponent(join(self.tempdir, 'storage'))
        self.jazz = OaiJazzLucene(self._luceneIndex, self._storage, iter(xrange(9999)))

    def addDocuments(self, size):
        for id in range(1,size+1):
            self.jazz.add('%05d' %id, 'oai_dc', bind_string('<title>The Title %d</title>' %id))

    def testListAll(self):
        self.addDocuments(1)
        result = self.jazz.oaiSelect(None, 'oai_dc', '0', None, None)
        result2 = self.jazz.listAll()
        self.assertEquals(['00001'], list(result2))
        self.assertEquals(['00001'], list(result))

    def testListRecordsWith2000(self):
        BooleanQuery.setMaxClauseCount(10) # Cause an early TooManyClauses exception.
        self.addDocuments(50)
        result = self.jazz.oaiSelect(None, 'oai_dc', '0', None, None)
        first = iter(result).next()
        self.assertEquals('00001', first)
        result = self.jazz.oaiSelect(None, 'oai_dc', '%020d' % 1, None, None)
        first = iter(result).next()
        self.assertEquals('00002', first)
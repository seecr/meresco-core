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
from time import strftime, gmtime, sleep
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

    def tearDown(self):
        self.realjazz.close()
        CQ2TestCase.tearDown(self)

    def testAdd(self):
        self.mockedjazz.add(self.id, self.partName, bind_string('<empty/>'))
        self.assertEquals(2,len(self.index.calledMethods))
        self.assertEquals("deleteID('id')", str(self.index.calledMethods[0]))
        self.assertEquals('addToIndex(<meresco.components.lucene.document.Document>)', str(self.index.calledMethods[1]))

    def testDeleteIncrementsDatestampAndUnique(self):
        jazz = self.realjazz
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>%s</setSpec></header>'
        jazz.add('23', 'oai_dc', bind_string('<nothing/>'), bind_string(header % 'aSet').header)
        stamp = jazz.getDatestamp('23')
        unique = jazz.getUnique('23')
        sleep(1)
        jazz.delete('23')
        self.assertNotEqual(stamp,  jazz.getDatestamp('23'))
        self.assertEquals(int(unique)+1, int(jazz.getUnique('23')))

    def testListRecordsNoResults(self):
        jazz = self.realjazz
        result = jazz.oaiSelect(None, 'xxx', '0', None, None)
        self.assertEquals([], result)

    def testGetUnique(self):
        def getStream(id, partName):
            yield """<oaimeta>
        <stamp>DATESTAMP_FOR_TEST</stamp>
        <unique>UNIQUE_FOR_TEST</unique>
		<sets/>
		<prefixes/>
    </oaimeta>"""
        self.storage.getStream = getStream
        self.storage.isAvailable = lambda id, part: (True, True)
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
        jazz.add('123', 'oai_dc', bind_string('<empty/>'), bind_string(header % 1).header)
        jazz.add('124', 'oai_dc', bind_string('<empty/>'), bind_string(header % 2).header)
        results =jazz.oaiSelect('1', 'oai_dc', '0', None, None)
        self.assertEquals(1, len(results))
        results =jazz.oaiSelect('2', 'oai_dc', '0', None, None)
        self.assertEquals(1, len(results))
        results =jazz.oaiSelect(None, 'oai_dc', '0', None, None)
        self.assertEquals(2, len(results))

    def testAddRecognizeNamespace(self):
        header = '<header xmlns="this.is.not.the.right.ns"><setSpec>%s</setSpec></header>'
        jazz = self.realjazz
        jazz.add('123', 'oai_dc', bind_string('<empty/>'), bind_string(header % 1).header)
        results =jazz.oaiSelect('1', 'oai_dc', '0', None, None)
        self.assertEquals(0, len(results))
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>%s</setSpec></header>'
        jazz.add('124', 'oai_dc', bind_string('<empty/>'), bind_string(header % 1).header)
        results =jazz.oaiSelect('1', 'oai_dc', '0', None, None)
        self.assertEquals(1, len(results))

    def testAddWithoutData(self):
        jazz = self.realjazz
        jazz.add('9', 'oai_cd', bind_string('<empty/>'))


    def testMultipleHierarchicalSets(self):
        spec = "<setSpec>%s</setSpec>"
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/">%s</header>'
        jazz = self.realjazz
        jazz.add('124', 'oai_dc', bind_string('<empty/>'), bind_string(header % (spec % '2:3' + spec % '3:4')).header)
        self.assertEquals(1, len(jazz.oaiSelect('2', 'oai_dc', '0', None, None)))
        self.assertEquals(1, len(jazz.oaiSelect('2:3', 'oai_dc', '0', None, None)))
        self.assertEquals(1, len(jazz.oaiSelect('3', 'oai_dc', '0', None, None)))
        self.assertEquals(1, len(jazz.oaiSelect('3:4', 'oai_dc', '0', None, None)))

    def testGetSets(self):
        jazz = self.realjazz
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>%s</setSpec></header>'
        jazz.add('124', 'oai_dc', bind_string('<empty/>'), bind_string(header % 1).header)
        sets = jazz.getSets('124')
        self.assertEquals(['1'], sets)
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>%s</setSpec></header>'
        jazz.add('125', 'oai_dc', bind_string('<empty/>'), bind_string(header % 2).header)
        sets = jazz.getSets('125')
        self.assertEquals(['2'], sets)
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>1:2</setSpec><setSpec>2</setSpec></header>'
        jazz.add('124', 'oai_dc', bind_string('<empty/>'), bind_string(header).header)
        sets = jazz.getSets('124')
        self.assertEquals(['1', '1:2', '2'], sets)

    def testSetSpecWithTokensSplit(self):
        jazz = self.realjazz
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>%s</setSpec></header>'
        jazz.add('124', 'oai_dc', bind_string('<empty/>'), bind_string(header % "1:23").header)
        results = jazz.oaiSelect('1:23', 'oai_dc', '0', None, None)
        self.assertEquals(1, len(results))

    def testDelete(self):
        jazz = self.realjazz
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>%s</setSpec></header>'
        jazz.add('123', 'oai_dc', bind_string('<empty/>'), bind_string(header % "1").header)
        self.assertFalse(jazz.isDeleted('123'))
        self.assertEquals(1, len(jazz.oaiSelect(None, 'oai_dc', '0', None, None)))
        jazz.delete('123')
        self.assertTrue(jazz.isDeleted('123'))
        self.assertEquals(1, len(jazz.oaiSelect(None, 'oai_dc', '0', None, None)))

    def testDeleteAndReAdd(self):
        jazz = self.realjazz
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>%s</setSpec></header>'
        jazz.add('123', 'oai_dc', bind_string('<empty/>'), bind_string(header % "1").header)
        jazz.delete('123')
        jazz.add('123', 'oai_dc', bind_string('<empty/>'), bind_string(header % "1").header)
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
        jazz.add('456', 'oai_dc', bind_string('<empty/>'), bind_string(header % 'set1').header)
        jazz.add('457', 'oai_dc', bind_string('<empty/>'), bind_string(header % 'set2').header)
        jazz.add('458', 'oai_dc', bind_string('<empty/>'), bind_string(header % 'set3').header)
        sets = jazz.listSets()
        self.assertEquals(['set1', 'set2', 'set3'], sets)

    def testHierarchicalSets(self):
        jazz = self.realjazz
        header = '<header xmlns="http://www.openarchives.org/OAI/2.0/"><setSpec>%s</setSpec></header>'
        jazz.add('456', 'oai_dc', bind_string('<empty/>'), bind_string(header % 'set1:set2:set3').header)
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
             xsi:schemaLocation="http://oai_dc http://oai_dc/dc.xsd"/>').dc)
        prefixes = jazz.getAllPrefixes()
        self.assertEquals([('oai_dc', 'http://oai_dc/dc.xsd', 'http://oai_dc')], list(prefixes))
        jazz.add('457', 'dc2', bind_string('<oai_dc:dc xmlns:oai_dc="http://dc2"/>').dc)
        prefixes = jazz.getAllPrefixes()
        self.assertEquals(set([('oai_dc', 'http://oai_dc/dc.xsd', 'http://oai_dc'), ('dc2', '', 'http://dc2')]), prefixes)

    def testMetadataPrefixesFromRootTag(self):
        jazz = self.realjazz
        jazz.add('456', 'oai_dc', bind_string('<oai_dc:dc xmlns:oai_dc="http://oai_dc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
             xsi:schemaLocation="http://oai_dc http://oai_dc/dc.xsd"/>'))
        prefixes = jazz.getAllPrefixes()
        self.assertEquals([('oai_dc', 'http://oai_dc/dc.xsd', 'http://oai_dc')], list(prefixes))

    def testIncompletePrefixInfo(self):
        jazz = self.realjazz
        jazz.add('457', 'dc2', bind_string('<oai_dc/>').oai_dc)
        prefixes = jazz.getAllPrefixes()
        self.assertEquals(set([('dc2', '', '')]), prefixes)

    def testPreserveRicherPrefixInfo(self):
        jazz = self.realjazz
        jazz.add('457', 'oai_dc', bind_string('<oai_dc:dc xmlns:oai_dc="http://oai_dc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
             xsi:schemaLocation="http://oai_dc http://oai_dc/dc.xsd"/>').dc)
        jazz.add('457', 'oai_dc', bind_string('<oai_dc/>'))
        prefixes = jazz.getAllPrefixes()
        self.assertEquals(set([('oai_dc', 'http://oai_dc/dc.xsd', 'http://oai_dc')]), prefixes)


class OaiJazzLuceneIntegrationTest(CQ2TestCase):
    def setUp(self):
        CQ2TestCase.setUp(self)
        self._luceneIndex = LuceneIndex(join(self.tempdir, "lucene-index"))
        self._storage = StorageComponent(join(self.tempdir, 'storage'))
        self.jazz = OaiJazzLucene(self._luceneIndex, self._storage, iter(xrange(9999)))

    def addDocuments(self, size):
        for id in range(1,size+1):
            self._addRecord(id)

    def _addRecord(self, anId):
        self.jazz.add('%05d' % anId, 'oai_dc', bind_string('<title>The Title %d</title>' % anId))

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

    def testListRecordsWithFromAndUntil(self):
        BooleanQuery.setMaxClauseCount(10) # Cause an early TooManyClauses exception.
        self.jazz._gettime = lambda: (2007, 9, 24, 14, 27, 53, 0, 267, 0)
        self._addRecord(1)
        self.jazz._gettime = lambda: (2007, 9, 23, 14, 27, 53, 0, 267, 0)
        self._addRecord(2)
        self.jazz._gettime = lambda: (2007, 9, 22, 14, 27, 53, 0, 267, 0)
        self._addRecord(3)
        self.jazz._gettime = lambda: (2007, 9, 21, 14, 27, 53, 0, 267, 0)
        self._addRecord(4)

        result = list(self.jazz.oaiSelect(None, 'oai_dc', '0', "2007-09-22T00:00:00Z", None))
        self.assertEquals(3, len(result))
        result = list(self.jazz.oaiSelect(None, 'oai_dc', '0', "2007-09-22", "2007-09-23"))
        self.assertEquals(2, len(result))

    def testFixUntil(self):
        self.assertEquals("2007-09-22T12:33:00Z", self.jazz._fixUntilDate("2007-09-22T12:33:00Z"))
        self.assertEquals("2007-09-23T00:00:00Z", self.jazz._fixUntilDate("2007-09-22"))
        self.assertEquals("2008-01-01T00:00:00Z", self.jazz._fixUntilDate("2007-12-31"))
        self.assertEquals("2004-02-29T00:00:00Z", self.jazz._fixUntilDate("2004-02-28"))
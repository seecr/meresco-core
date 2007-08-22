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
from cq2utils.cq2testcase import CQ2TestCase
from unittest import TestCase
from cq2utils.calltrace import CallTrace
from meresco.components.oai import OaiJazzLucene
from meresco.components.xml2document import TEDDY_NS, Xml2Document
from meresco.framework.observable import Observable
from amara import binderytools
from PyLucene import BooleanQuery
from storage import Storage
from os.path import join

from meresco.components.lucene.lucene import LuceneIndex
from meresco.components.oai.stampcomponent import STAMP_PART, DATESTAMP, UNIQUE
from meresco.components.lucene.document import Document
from meresco.components.oai.partscomponent import PARTS_PART, PART

FIELDS = binderytools.bind_string("""<xmlfields xmlns:teddy="%s">
    <field1>this is field1</field1>
    <untokenizedField teddy:tokenize="false">this should not be tokenized</untokenizedField>
</xmlfields>""" % TEDDY_NS).xmlfields

class OaiJazzLuceneTest(CQ2TestCase):
    def setUp(self):
        CQ2TestCase.setUp(self)
        self.index = CallTrace("Index")
        self.storage = CallTrace("Storage")
        self.oaijazz = OaiJazzLucene(self.index, self.storage)

        self.id = "id"
        self.partName = "xmlfields"
        self.document = Xml2Document()._create(self.id, FIELDS)

    def testAdd(self):
        self.oaijazz.add(self.id, self.partName, self.document)
        self.assertEquals(2,len(self.index.calledMethods))
        self.assertEquals("deleteID('id')", str(self.index.calledMethods[0]))
        self.assertEquals('addToIndex(<meresco.components.lucene.document.Document>)', str(self.index.calledMethods[1]))

    def testDelete(self):
        self.oaijazz.delete(self.id)

        self.assertEquals(1,len(self.index.calledMethods))
        self.assertEquals("deleteID('id')", str(self.index.calledMethods[0]))

    def testListRecords(self):
        self.oaijazz.oaiSelect(None, 'PART', '0', None, None)
        executeQueryMethod = self.index.calledMethods[0]
        self.assertEquals(2, len(executeQueryMethod.arguments))
        self.assertEquals('+__parts__.part:PART', str(executeQueryMethod.arguments[0]))
        self.assertEquals('__stamp__.unique', executeQueryMethod.arguments[1])

    def testListRecordsParams(self):
        self.oaijazz.oaiSelect('ONE:TWO:THREE', 'PART', '0010', '2000-01-01T00:00:00Z', '2000-31-12T00:00:00Z')
        executeQueryMethod = self.index.calledMethods[0]
        queryWrapper = executeQueryMethod.arguments[0]
        self.assertEquals(2, len(executeQueryMethod.arguments))
        self.assertEquals('+__parts__.part:PART +__stamp__.unique:{0010 TO *] +__stamp__.datestamp:[2000-01-01T00:00:00Z TO 2000-31-12T00:00:00Z] +__set_membership__.set:ONE:TWO:THREE', str(executeQueryMethod.arguments[0]))
        self.assertEquals('__stamp__.unique', executeQueryMethod.arguments[1])

    def testGetUnique(self):
        def write(sink, id, partName):
            sink.write("""<__stamp__>
        <datestamp>DATESTAMP_FOR_TEST</datestamp>
        <unique>UNIQUE_FOR_TEST</unique>
    </__stamp__>""")
        self.storage.write = write
        uniqueNumber = self.oaijazz.getUnique('somedocid')
        self.assertEquals('UNIQUE_FOR_TEST', uniqueNumber)

    def testGetSets(self):
        def write(sink, id, partName):
            sink.write("<__sets__><setSpec>aSet</setSpec><setSpec>anotherSet</setSpec></__sets__>")
        self.storage.write = write
        sets = self.oaijazz.getSets('somedocid')
        self.assertEquals(['aSet', 'anotherSet'], sets)

class OaiJazzLuceneIntegrationTest(CQ2TestCase):
    def setUp(self):
        CQ2TestCase.setUp(self)
        self._luceneIndex = LuceneIndex(join(self.tempdir, "lucene-index"))
        self._storage = Storage(join(self.tempdir, 'storage'))
        self.subject = OaiJazzLucene(self._luceneIndex, self._storage)


    def addDocuments(self, size):
        for i in range(1,size+1):
            d = Document('%05d' %  i)
            d.addIndexedField('title', 'The title')
            d.addIndexedField('%s.%s' % (PARTS_PART, PART), 'oai_dc', False)
            d.addIndexedField('%s.%s' % (STAMP_PART, UNIQUE), '%020d' % i)
            self._luceneIndex.addToIndex(d)
        self._luceneIndex.reOpen()

    def testListRecords(self):
        self.addDocuments(1)

        result = self.subject.oaiSelect(None, 'oai_dc', '0', None, None)
        result2 = self.subject.listAll()
        self.assertEquals(['00001'], list(result2))
        self.assertEquals(['00001'], list(result))

    def testListRecordsWith2000(self):
        BooleanQuery.setMaxClauseCount(10) # Cause an early TooManyClauses exception.
        self.addDocuments(50)

        result = self.subject.oaiSelect(None, 'oai_dc', '0', None, None)
        #self.assertEquals(200, len(list(result)))
        first = iter(result).next()
        self.assertEquals('00001', first)
        result = self.subject.oaiSelect(None, 'oai_dc', '%020d' % 1, None, None)
        first = iter(result).next()
        self.assertEquals('00002', first)

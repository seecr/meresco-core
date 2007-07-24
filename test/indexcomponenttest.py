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
from meresco.components.lucene.indexcomponent import IndexComponent
from meresco.components.xml2document import TEDDY_NS, Xml2Document
from meresco.framework.observable import Observable
from amara import binderytools
from PyLucene import BooleanQuery

from tempfile import mkdtemp, gettempdir
import os
from shutil import rmtree
from meresco.components.lucene.lucene import LuceneIndex
from meresco.components.stampcomponent import STAMP_PART, DATESTAMP, UNIQUE
from meresco.components.lucene.document import Document
from meresco.components.partscomponent import PARTS_PART, PART

FIELDS = binderytools.bind_string("""<xmlfields xmlns:teddy="%s">
    <field1>this is field1</field1>
    <untokenizedField teddy:tokenize="false">this should not be tokenized</untokenizedField>
</xmlfields>""" % TEDDY_NS).xmlfields

class IndexComponentTest(CQ2TestCase):
    def setUp(self):
        CQ2TestCase.setUp(self)
        self.index = CallTrace("Index")
        self.indexComponent = IndexComponent(self.index)
        
        self.id = "id"
        self.partName = "xmlfields"
        self.document = Xml2Document()._create(self.id, FIELDS)
        
    def testAdd(self):
        self.indexComponent.add(self.id, self.partName, self.document)
        self.assertEquals(2,len(self.index.calledMethods))
        self.assertEquals("deleteID('id')", str(self.index.calledMethods[0]))
        self.assertEquals('addToIndex(<meresco.components.lucene.document.Document>)', str(self.index.calledMethods[1]))
        
    def testDelete(self):
        self.indexComponent.delete(self.id)
        
        self.assertEquals(1,len(self.index.calledMethods))
        self.assertEquals("deleteID('id')", str(self.index.calledMethods[0]))
        
    def testListRecords(self):
        self.indexComponent.listRecords(partName = 'PART', sorted = None)
        executeQueryMethod = self.index.calledMethods[0]
        queryWrapper = executeQueryMethod.arguments[0]
        self.assertEquals('+__parts__.part:PART', str(queryWrapper.getPyLuceneQuery()))
        self.assertEquals(None, queryWrapper._sortBy)

    def testListRecordsSorted(self):
        self.indexComponent.listRecords(partName = 'PART', sorted = True)
        executeQueryMethod = self.index.calledMethods[0]
        queryWrapper = executeQueryMethod.arguments[0]
        self.assertEquals('+__parts__.part:PART', str(queryWrapper.getPyLuceneQuery()))
        self.assertEquals('__stamp__.unique', str(queryWrapper._sortBy))
    
    def testListRecordsParams(self):
        self.indexComponent.listRecords(partName = 'PART', continueAt = '0010', oaiFrom = '2000-01-01T00:00:00Z', oaiUntil = '2000-31-12T00:00:00Z', oaiSet = 'ONE:TWO:THREE', sorted = True)
        executeQueryMethod = self.index.calledMethods[0]
        queryWrapper = executeQueryMethod.arguments[0]
        self.assertEquals('+__parts__.part:PART +__stamp__.unique:{0010 TO *] +__stamp__.datestamp:[2000-01-01T00:00:00Z TO 2000-31-12T00:00:00Z] +__set_membership__.set:ONE:TWO:THREE', str(queryWrapper.getPyLuceneQuery()))
        self.assertEquals('__stamp__.unique', str(queryWrapper._sortBy))
        
class IndexComponentWithLuceneTest(TestCase):
    def setUp(self):
        self._tempdir = gettempdir()+'/testingit'
        self.directoryName = os.path.join(self._tempdir, 'lucene-index')
        os.path.isdir(self.directoryName) or os.makedirs(self.directoryName)
        self._luceneIndex = LuceneIndex(self.directoryName)
        self.subject = IndexComponent(self._luceneIndex)
        
    def tearDown(self):
        # remove references to the index before removing directory.
        del self._luceneIndex
        del self.subject
        if os.path.exists(self._tempdir):
            rmtree(self._tempdir)

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
        
        result = self.subject.listRecords('oai_dc')
        result2 = self.subject.listAll()
        self.assertEquals(['00001'], list(result2))
        self.assertEquals(['00001'], list(result))
        
    def testListRecordsWith2000(self):
        BooleanQuery.setMaxClauseCount(10) # Cause an early TooManyClauses exception.
        self.addDocuments(50)
        
        result = self.subject.listRecords('oai_dc')
        #self.assertEquals(200, len(list(result)))
        first = iter(result).next()
        self.assertEquals('00001', first)
        result = self.subject.listRecords('oai_dc', continueAt = '%020d' % 1)
        first = iter(result).next()
        self.assertEquals('00002', first)

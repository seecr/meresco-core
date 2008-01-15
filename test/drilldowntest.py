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
from PyLucene import Term, TermQuery, IndexReader

from cq2utils import CQ2TestCase

from meresco.components.lucene import Document
from meresco.components.drilldown import Drilldown
from meresco.components.lucene.lucene import LuceneIndex
from meresco.components.drilldown.lucenerawdocsets import LuceneRawDocSets

class DrilldownTest(CQ2TestCase):
    #Helper functions:
    def addUntokenized(self, documents):
        index = LuceneIndex(self.tempdir, 'CQL Composer ignored')
        for docId, fields in documents:
            myDocument = Document(docId)
            for field, value in fields.items():
                myDocument.addIndexedField(field, value, tokenize = False)
            index.addDocument(myDocument)
        index.close()

    def testLoadDocSetsNoTerms(self):
        data = [('field_0', [])]
        drilldown = Drilldown(['field_0'])
        drilldown.loadDocSets(data, 5)

        self.assertEquals(['field_0'], drilldown._docSets.keys())
        self.assertEquals(0, len(drilldown._docSets['field_0']))
        field, results = drilldown.drilldown([0], [('field_0', 10)]).next()
        self.assertEquals('field_0', field)
        self.assertEquals(0, len(list(results)))

    def testLoadDocSets(self):
        data = [('field_0', [('term_0', [1,2,5]), ('term_1', [4])])]

        drilldown = Drilldown(['field_0'])
        drilldown.loadDocSets(data, 5)

        self.assertEquals(2, len(drilldown._docSets['field_0']))
        self.assertEquals(3, dict(drilldown._docSets['field_0'])['term_0'].cardinality())
        self.assertEquals(1, dict(drilldown._docSets['field_0'])['term_1'].cardinality())

    def testLoadDocSetsOverwritesPreviousDocsets(self):
        data1 = [('field_0', [('term_0', [1,2,5]), ('term_1', [4])])]
        data2 = [('field_0', [('term_0', [1]), ('term_2', [2,4])])]

        drilldown = Drilldown(['field_0'])
        drilldown.loadDocSets(data1, 5)
        drilldown.loadDocSets(data2, 5)
        self.assertEquals(2, len(drilldown._docSets['field_0']))
        self.assertEquals(1, dict(drilldown._docSets['field_0'])['term_0'].cardinality())
        self.assertFalse(dict(drilldown._docSets['field_0']).has_key('term_1'))
        self.assertEquals(2, dict(drilldown._docSets['field_0'])['term_2'].cardinality())

    def testIndexOptimized(self):
        self.addUntokenized([('id', {'field_0': 'this is term_0'})])
        drilldown = Drilldown(['field_0'])
        reader = IndexReader.open(self.tempdir)
        drilldown.indexOptimized(reader)
        field, results = drilldown.drilldown([0], [('field_0', 10)]).next()
        self.assertEquals('field_0', field)
        self.assertEquals([('this is term_0', 1)], list(results))
    
    def testDrilldown(self):
        self.addUntokenized([
            ('1', {'field_0': 'this is term_0', 'field_1': 'inquery'}),
            ('2', {'field_0': 'this is term_1', 'field_1': 'inquery'}),
            ('3', {'field_0': 'this is term_1', 'field_1': 'inquery'}),
            ('4', {'field_0': 'this is term_2', 'field_1': 'cannotbefound'})])
        reader = IndexReader.open(self.tempdir)
        convertor = LuceneRawDocSets(reader, ['field_0', 'field_1'])
        drilldown = Drilldown(['field_0', 'field_1'])
        drilldown.loadDocSets(convertor.getDocSets(), convertor.docCount())
        index = LuceneIndex(self.tempdir, 'CQL composer not used')        
        queryResults = index.executeQuery(TermQuery(Term("field_1", "inquery")))
        self.assertEquals(3, len(queryResults))

        drilldownResult = list(drilldown.drilldown(queryResults.docNumbers(), [('field_0', 0), ('field_1', 0)]))

        self.assertEquals(2, len(drilldownResult))
        result = dict(drilldownResult)
        self.assertEquals(['field_0', 'field_1'], result.keys())
        self.assertEquals([("this is term_1", 2), ("this is term_0", 1)], list(result['field_0']))
        self.assertEquals([("inquery", 3)], list(result['field_1']))


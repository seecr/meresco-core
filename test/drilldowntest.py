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
from PyLucene import Term, TermQuery, IndexReader, MatchAllDocsQuery

from cq2utils import CQ2TestCase, CallTrace

from meresco.components.lucene import Document
from meresco.components.drilldown import Drilldown, DrilldownFieldnames
from meresco.components.drilldown.drilldown import FieldMatrix
from meresco.components.lucene.lucene import LuceneIndex
from meresco.components.lucene.lucenerawdocsets import LuceneRawDocSets

from timerfortestsupport import TimerForTestSupport

from bitmatrix import Row

class DrilldownTest(CQ2TestCase):

    def setUp(self):
        CQ2TestCase.setUp(self)
        self.index = LuceneIndex(self.tempdir, timer=TimerForTestSupport())

    def tearDown(self):
        self.index.close()
        CQ2TestCase.tearDown(self)

    #Helper functions:
    def addUntokenized(self, documents):
        for docId, fields in documents:
            myDocument = Document(docId)
            for field, value in fields.items():
                myDocument.addIndexedField(field, value, tokenize = False)
            self.index.addDocument(myDocument)

    def testIndexStarted(self):
        self.addUntokenized([('id', {'field_0': 'this is term_0'})])
        drilldown = Drilldown(['field_0'])
        reader = IndexReader.open(self.tempdir)
        drilldown.indexStarted(reader)
        field, results = drilldown.drilldown(Row([0]), [('field_0', 10, False)]).next()
        self.assertEquals('field_0', field)
        self.assertEquals([('this is term_0', 1)], list(results))

    def testDrilldown(self):
        self.addUntokenized([
            ('0', {'field_0': 'this is term_0', 'field_1': 'inquery'}),
            ('1', {'field_0': 'this is term_1', 'field_1': 'inquery'}),
            ('2', {'field_0': 'this is term_1', 'field_1': 'inquery'}),
            ('3', {'field_0': 'this is term_2', 'field_1': 'cannotbefound'})])
        reader = IndexReader.open(self.tempdir)
        convertor = LuceneRawDocSets(reader, ['field_0', 'field_1'])
        drilldown = Drilldown(['field_0', 'field_1'])
        drilldown.loadDocSets(convertor.getDocSets())
        total, queryResults = self.index.executeQuery(TermQuery(Term("field_1", "inquery")))
        self.assertEquals(3, total)

        drilldownResult = list(drilldown.drilldown(self.index.bitMatrixRow(TermQuery(Term("field_1", "inquery"))), [('field_0', 0, False), ('field_1', 0, False)]))

        self.assertEquals(2, len(drilldownResult))
        result = dict(drilldownResult)
        self.assertEquals(['field_0', 'field_1'], result.keys())
        self.assertEquals(set([("this is term_0", 1), ("this is term_1", 2)]), set(result['field_0']))
        self.assertEquals([("inquery", 3)], list(result['field_1']))

    def testSorting(self):
        self.addUntokenized([
            ('0', {'field0': 'term1'}),
            ('1', {'field0': 'term1'}),
            ('2', {'field0': 'term2'}),
            ('3', {'field0': 'term0'})])
        reader = IndexReader.open(self.tempdir)
        convertor = LuceneRawDocSets(reader, ['field0'])
        drilldown = Drilldown(['field0'])
        drilldown.loadDocSets(convertor.getDocSets())
        queryResults = self.index.executeQuery(MatchAllDocsQuery())
        ddData = list(drilldown.drilldown(self.index.bitMatrixRow(MatchAllDocsQuery()), [('field0', 0, False)]))
        self.assertEquals([('term0',1), ('term1',2), ('term2',1)], ddData[0][1])
        ddData = list(drilldown.drilldown(self.index.bitMatrixRow(MatchAllDocsQuery()), [('field0', 0, True)]))
        self.assertEquals([('term1',2), ('term0',1), ('term2',1)], ddData[0][1])


    def testAppendToRow(self):
        fieldMatrix = FieldMatrix([])

        fieldMatrix.addDocument(0, ['term0', 'term1'])
        self.assertEquals('term0', fieldMatrix._row2term[0])
        self.assertEquals('term1', fieldMatrix._row2term[1])
        self.assertEquals([('term0', 1), ('term1', 1)], list(fieldMatrix.drilldown(Row([0, 1]))))

        fieldMatrix.addDocument(1, ['term0', 'term1'])
        self.assertEquals('term0', fieldMatrix._row2term[0])
        self.assertEquals('term1', fieldMatrix._row2term[1])
        self.assertEquals([('term0', 2), ('term1', 2)], list(fieldMatrix.drilldown(Row([0, 1]))))

        fieldMatrix.addDocument(2, ['term0', 'term2'])
        self.assertEquals([('term0', 3), ('term1', 2), ('term2', 1)], list(fieldMatrix.drilldown(Row([0, 1, 2]))))

        try:
            fieldMatrix.addDocument(2, ['term0', 'term2'])
        except Exception, e:
            self.assertTrue("non-increasing" in str(e))

    def testDynamicDrilldownFields(self):
        self.addUntokenized([
            ('0', {'field_0': 'this is term_0', 'field_1': 'inquery'}),
            ('1', {'field_0': 'this is term_1', 'field_1': 'inquery'}),
            ('2', {'field_0': 'this is term_1', 'field_1': 'inquery'}),
            ('3', {'__private_field': 'this is term_2', 'field_1': 'cannotbefound'})])
        reader = IndexReader.open(self.tempdir)
        drilldown = Drilldown()
        drilldown.indexStarted(reader)
        hits = self.index.bitMatrixRow(MatchAllDocsQuery())
        results = list(drilldown.drilldown(hits, [('field_0', 0, False)]))
        self.assertEquals('field_0', results[0][0])
        results = list(drilldown.drilldown(hits))
        self.assertEquals('field_0', results[0][0])
        self.assertEquals('field_1', results[1][0])
        self.assertEquals(2, len(results))

    def testFieldGetAdded(self):
        self.addUntokenized([
            ('0', {'field_0': 'this is term_0'})
        ])
        drilldown = Drilldown()
        drilldown.indexStarted(self.index.getIndexReader())
        hits = self.index.bitMatrixRow(MatchAllDocsQuery())
        results = list(drilldown.drilldown(hits))
        self.assertEquals('field_0', results[0][0])
        self.assertEquals(1, len(results))
        self.addUntokenized([
            ('1', {'field_0': 'this is term_0', 'field_1': 'inquery'})
        ])
        drilldown.indexStarted(self.index.getIndexReader())
        hits = self.index.bitMatrixRow(MatchAllDocsQuery())
        results = list(drilldown.drilldown(hits))
        self.assertEquals(2, len(results))
        self.assertEquals('field_0', results[0][0])
        self.assertEquals('field_1', results[1][0])

    def testDrilldownFieldnames(self):
        d = DrilldownFieldnames(
            lookup=lambda name: 'drilldown.'+name,
            reverse=lambda name: name[len('drilldown.'):])
        observer = CallTrace('drilldown')
        observer.returnValues['drilldown'] = [('drilldown.field1', [('term1',1)]),('drilldown.field2', [('term2', 2)])]
        d.addObserver(observer)
        hits = CallTrace('Hits')

        result = list(d.drilldown(hits, [('field1', 0, True),('field2', 3, False)]))

        self.assertEquals(1, len(observer.calledMethods))
        self.assertEquals([('drilldown.field1', 0, True),('drilldown.field2', 3, False)], list(observer.calledMethods[0].args[1]))

        self.assertEquals([('field1', [('term1',1)]),('field2', [('term2', 2)])], result)

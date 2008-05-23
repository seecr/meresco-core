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

from cq2utils import CQ2TestCase, CallTrace

from meresco.components.lucene import Document
from meresco.components.drilldown import Drilldown
from meresco.components.drilldown.drilldown import FieldMatrix
from meresco.components.lucene.lucene import LuceneIndex
from meresco.components.drilldown.lucenerawdocsets import LuceneRawDocSets

from timerfortestsupport import TimerForTestSupport

from bitmatrix import Row

class DrilldownTest(CQ2TestCase):
    #Helper functions:
    def addUntokenized(self, documents):
        index = LuceneIndex(self.tempdir, 'CQL Composer ignored', timer=TimerForTestSupport())
        for docId, fields in documents:
            myDocument = Document(docId)
            for field, value in fields.items():
                myDocument.addIndexedField(field, value, tokenize = False)
            index.addDocument(myDocument)
        index.close()

#de volgende drie tests moeten ofwel verschoven worden naar FieldMatrix, ofwel gewoon weggegooid

    #def testLoadDocSetsNoTerms(self):
        #data = [('field_0', [])]
        #drilldown = Drilldown(['field_0'])
        #drilldown.loadDocSets(data)

        #self.assertEquals(['field_0'], drilldown._docSets.keys())
        #self.assertEquals(0, len(drilldown._docSets['field_0']))
        #field, results = drilldown.drilldown(Row([0]), [('field_0', 10)]).next()
        #self.assertEquals('field_0', field)
        #self.assertEquals(0, len(list(results)))

    #def testLoadDocSets(self):
        #data = [('field_0', [('term_0', [1,2,5]), ('term_1', [4])])]

        #drilldown = Drilldown(['field_0'])
        #drilldown.loadDocSets(data)



        #self.assertEquals(2, len(drilldown._docSets['field_0']))
        #self.assertEquals(3, dict(drilldown._docSets['field_0'])['term_0'].cardinality())
        #self.assertEquals(1, dict(drilldown._docSets['field_0'])['term_1'].cardinality())

    #def testLoadDocSetsOverwritesPreviousDocsets(self):
        #data1 = [('field_0', [('term_0', [1,2,5]), ('term_1', [4])])]
        #data2 = [('field_0', [('term_0', [1]), ('term_2', [2,4])])]

        #drilldown = Drilldown(['field_0'])
        #drilldown.loadDocSets(data1)
        #drilldown.loadDocSets(data2)
        #self.assertEquals(2, len(drilldown._docSets['field_0']))
        #self.assertEquals(1, dict(drilldown._docSets['field_0'])['term_0'].cardinality())
        #self.assertFalse(dict(drilldown._docSets['field_0']).has_key('term_1'))
        #self.assertEquals(2, dict(drilldown._docSets['field_0'])['term_2'].cardinality())

    def testIndexStarted(self):
        self.addUntokenized([('id', {'field_0': 'this is term_0'})])
        drilldown = Drilldown(['field_0'])
        reader = IndexReader.open(self.tempdir)
        drilldown.indexStarted(reader)
        field, results = drilldown.drilldown(Row([0]), [('field_0', 10)]).next()
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
        index = LuceneIndex(self.tempdir, 'CQL composer not used', timer=CallTrace())
        index._reopenIndex()
        queryResults = index.executeQuery(TermQuery(Term("field_1", "inquery")))
        self.assertEquals(3, len(queryResults))

        drilldownResult = list(drilldown.drilldown(queryResults.bitMatrixRow(), [('field_0', 0), ('field_1', 0)]))

        self.assertEquals(2, len(drilldownResult))
        result = dict(drilldownResult)
        self.assertEquals(['field_0', 'field_1'], result.keys())
        self.assertEquals(set([("this is term_0", 1), ("this is term_1", 2)]), set(result['field_0']))
        self.assertEquals([("inquery", 3)], list(result['field_1']))

    def testAppendToRow(self):
        fieldMatrix = FieldMatrix([])

        fieldMatrix.addDocument(0, ['term0', 'term1'])
        self.assertEquals('term0', fieldMatrix._trie.getTerm(0))
        self.assertEquals('term1', fieldMatrix._trie.getTerm(1))
        self.assertEquals([('term0', 1), ('term1', 1)], list(fieldMatrix.drilldown(Row([0, 1]))))

        fieldMatrix.addDocument(1, ['term0', 'term1'])
        self.assertEquals('term0', fieldMatrix._trie.getTerm(0))
        self.assertEquals('term1', fieldMatrix._trie.getTerm(1))
        self.assertEquals([('term0', 2), ('term1', 2)], list(fieldMatrix.drilldown(Row([0, 1]))))

        fieldMatrix.addDocument(2, ['term0', 'term2'])
        self.assertEquals([('term0', 3), ('term1', 2), ('term2', 1)], list(fieldMatrix.drilldown(Row([0, 1, 2]))))

        try:
            fieldMatrix.addDocument(2, ['term0', 'term2'])
        except Exception, e:
            self.assertTrue("non-increasing" in str(e))

    def testSterretje(self):
        self.addUntokenized([
            ('0', {'field_0': 'this is term_0', 'field_1': 'inquery'}),
            ('1', {'field_0': 'this is term_1', 'field_1': 'inquery'}),
            ('2', {'field_0': 'this is term_1', 'field_1': 'inquery'}),
            ('3', {'field_0': 'this is term_2', 'field_1': 'cannotbefound'}),
            ('4', {'field_0': 'this has different prefix', 'field_1': 'inquery'}),
            ])
        reader = IndexReader.open(self.tempdir)
        convertor = LuceneRawDocSets(reader, ['field_0', 'field_1'])
        drilldown = Drilldown(['field_0', 'field_1'])
        drilldown.loadDocSets(convertor.getDocSets())
        index = LuceneIndex(self.tempdir, 'CQL composer not used', timer=CallTrace())
        index._reopenIndex()
        queryResults = index.executeQuery(TermQuery(Term("field_1", "inquery")))
        self.assertEquals(4, len(queryResults))

        self.assertEquals([('this has different prefix', 1), ('this is term_0', 1), ('this is term_1', 2)], list(drilldown.sterretje("field_0", "this", queryResults.bitMatrixRow())))

        self.assertEquals([('this is term_0', 1), ('this is term_1', 2)], list(drilldown.sterretje("field_0", "this is", queryResults.bitMatrixRow())))


    def testDrilldownBitwiseAddIntegration(self):

        #"""This Test was created by KvS/JJ on 29/02/2008 and has a limited life span. It is bloated because we didn't understand everything yet. Feel free to toss it"""
        from meresco.components.dictionary import DocumentDict, DocumentField, Dict2Doc
        from PyLucene import MatchAllDocsQuery
        from cq2utils import CallTrace

        index = LuceneIndex(self.tempdir, 'CQL composer not used', timer=CallTrace(""), bitwise=True)
        drilldown = Drilldown(['value'])
        drilldown.loadDocSets([("value", [])])
        index.addObserver(drilldown)

        def add(id, value):
            dd = DocumentDict()
            dd.add("value", value)
            doc = Dict2Doc()._dict2Doc(id, dd)
            index.addDocument(doc)

        def assertDrilldown(expected, query):
            row = index.executeQuery(query).bitMatrixRow()
            results = list(drilldown.drilldown(row, [('value', 0)]))
            self.assertEquals(1, len(results))
            fieldname, result = results[0]
            self.assertEquals(expected, list(result))

        def values(l):
            return [('value%s' % i, 1) for i in l]

        for i in range(20):
            add('id%s' % i, 'value%s' % i)
        index._reopenIndex()

        assertDrilldown(values(range(20)), MatchAllDocsQuery())
        for i in range(20):
            assertDrilldown(values([i]), TermQuery(Term("value", "value%s" % i)))

        whatsLeft = range(20)
        for id in [0, 4 ,8, 11, 18, 19]:
            index.delete("id%s" % id)
            whatsLeft.remove(id)

        index._reopenIndex()

        assertDrilldown(values(whatsLeft), MatchAllDocsQuery())
        for i in whatsLeft:
            assertDrilldown(values([i]), TermQuery(Term("value", "value%s" % i)))

        for i in range(20, 110):
            add('id%s' % i, 'value%s' % i)
        index._reopenIndex()

        index._executeQuery(MatchAllDocsQuery()).bitMatrixRow().asList()

        whatsLeft = whatsLeft + range(20, 110)
        assertDrilldown(values(whatsLeft), MatchAllDocsQuery())
        for i in whatsLeft:
            assertDrilldown(values([i]), TermQuery(Term("value", "value%s" % i)))

        for i in range(110, 120):
            add('id%s' % i, 'value%s' % i)
        whatsLeft = whatsLeft + range(110, 120)

        index.delete("id%s" % 115)
        whatsLeft.remove(115)
        index._reopenIndex()

        assertDrilldown(values(whatsLeft), MatchAllDocsQuery())
        for i in whatsLeft:
            assertDrilldown(values([i]), TermQuery(Term("value", "value%s" % i)))
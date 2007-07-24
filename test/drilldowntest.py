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
import os.path
from tempfile import gettempdir
from shutil import rmtree
from PyLucene import Term, TermQuery

from unittest import TestCase
from convertertest import addUntokenized

from meresco.components.lucene.lucene import LuceneIndex
from meresco.components.lucene.converter import Converter
from meresco.components.drilldown.drilldown import DrillDown
from meresco.components.lucene.querywrapper import QueryWrapper

class DrillDownTest(TestCase):

    def setUp(self):
        self._tempdir = gettempdir() + '/testing'
        self._directoryName = os.path.join(self._tempdir, 'lucene-index')
        self._luceneIndex = LuceneIndex(self._directoryName)

    def tearDown(self):
        self._luceneIndex = None
        rmtree(self._tempdir)

    def testLoadDocSetsNoTerms(self):
        data = [('field_0', [])]
        drillDown = DrillDown(['field_0'])
        drillDown.loadDocSets(data, 5)

        self.assertEquals(['field_0'], drillDown._docSets.keys())
        self.assertEquals(0, len(drillDown._docSets['field_0']))
    
    def testLoadDocSets(self):
        data = [('field_0', [('term_0', [1,2,5]), ('term_1', [4])])]

        drillDown = DrillDown(['field_0'])
        drillDown.loadDocSets(data, 5)

        self.assertEquals(2, len(drillDown._docSets['field_0']))
        self.assertEquals(3, dict(drillDown._docSets['field_0'])['term_0'].cardinality())
        self.assertEquals(1, dict(drillDown._docSets['field_0'])['term_1'].cardinality())

    def testDrillDown(self):
        addUntokenized(self._luceneIndex, [
            ('1', {'field_0': 'this is term_0', 'field_1': 'inquery'}),
            ('2', {'field_0': 'this is term_0', 'field_1': 'inquery'}),
            ('3', {'field_0': 'this is term_1', 'field_1': 'inquery'}),
            ('4', {'field_0': 'this is term_2', 'field_1': 'cannotbefound'})])

        convertor = Converter(self._luceneIndex._getReader(), ['field_0', 'field_1'])
        drillDown = DrillDown(['field_0', 'field_1'])
        drillDown.loadDocSets(convertor.getDocSets(), convertor.docCount())

        queryResults = self._luceneIndex.executeQuery(QueryWrapper(TermQuery(Term("field_1", "inquery"))))
        self.assertEquals(3, len(queryResults))

        drilldownResult = drillDown.process(queryResults.getLuceneDocIds(), [('field_0', 0), ('field_1', 0)])

        self.assertEquals(2, len(drilldownResult))
        result = dict(drilldownResult)
        self.assertEquals(['field_0', 'field_1'], result.keys())
        self.assertEquals([("this is term_0", 2), ("this is term_1", 1)], result['field_0'])
        self.assertEquals([("inquery", 3)], result['field_1'])

class OldStuffForReference:
    def setUp(self):
        self._tempdir = gettempdir() + '/testing'
        self._directoryName = os.path.join(self._tempdir, 'lucene-index')
        self._luceneIndex = LuceneIndex(self._directoryName)

    def performQuery(self, queryString, sortBy = None, sortDescending = False):
        queryWrapper = QueryWrapper(queryString, sortBy, sortDescending)
        hitsWrapper = self._luceneIndex.executeQuery(queryWrapper)
        return hitsWrapper

    def testDrillDown(self):
        #self._luceneIndex._untokenizedTwinFieldnames = ['author', 'title']
        #self._luceneIndex._drillDownFieldnames = ['author', 'title']

        self.add([
            ('1', {'field_1': 'eerste titel', 'field_2': 'term_1'}),
            ('2', {'field_1': 'tweede titel', 'field_2': 'term_1'}),
            ('3', {'field_1': 'derde titel', 'field_2': 'tErM_2'}),
            ('4', {'field_1': 'geen tiiitel', 'field_2': 'tErM_2'})])
        self._luceneIndex.reloadBitArrays()

        self.assertEquals(2, len(self._luceneIndex._bitArrays['field_2']))
        self.assertEquals(4, len(self._luceneIndex._bitArrays['field_1']))

        documentHits = self.performQuery('field_1:titel')
        self.assertEquals(3, len(documentHits))

        drillDownResults = self._luceneIndex.drillDown(documentHits, drillDownFieldnamesAndMaximumResults = [('author', 0)])
        self.assertEquals({'author': [(u'Beer', 2), (u'Cats', 1)]}, drillDownResults)

        drillDownResults = self._luceneIndex.drillDown(documentHits, drillDownFieldnamesAndMaximumResults = [('author', 1)])
        self.assertEquals({'author': [(u'Beer', 2)]}, drillDownResults)


    def testDrillDownEmptyIndex(self):
        self._luceneIndex._untokenizedTwinFieldnames = ['author']
        self._luceneIndex._drillDownFieldnames = ['author']

        self._luceneIndex.reloadBitArrays()

        self.assertEquals(0, len(self._luceneIndex._bitArrays['author']))

        documentHits = self.performQuery('title:titel')

        drillDownResults = self._luceneIndex.drillDown(documentHits, drillDownFieldnamesAndMaximumResults = [('author', 0)])
        self.assertEquals({'author': []}, drillDownResults)

    def testLazyDrillDownAndCountField(self):
        self._luceneIndex._untokenizedTwinFieldnames = ['afieldname']
        self._luceneIndex._drillDownFieldnames = ['afieldname']
        bitarrays = [
            ("term0", MockBitArray([0, 1, 2, 3, 4])),
            ("term1", MockBitArray([10, 11, 12, 13, 14])),

            ("term2", MockBitArray([0, 1, 2])),
            ("term3", MockBitArray([10, 11, 12])),

            ("term4", MockBitArray([0])),
            ("term5", MockBitArray([10])),
        ]
        self._luceneIndex._bitArrays['afieldname'] = bitarrays

        queryBitArray = MockBitArray([0, 1, 2, 3, 4])

        result = self._luceneIndex.countField("afieldname", queryBitArray, 2)
        self.assertEquals([("term0", 5), ("term2", 3)], result)

        self.assertTrue(bitarrays[4][1]._cardinalityCalled)
        self.assertFalse(bitarrays[4][1]._combinedCardinalityCalled)
        self.assertFalse(bitarrays[5][1]._cardinalityCalled)
        self.assertFalse(bitarrays[5][1]._combinedCardinalityCalled)

        result = self._luceneIndex.countField("afieldname", queryBitArray, 0)
        self.assertEquals([("term0", 5), ("term2", 3), ("term4", 1)], result)

        result = self._luceneIndex.countField("afieldname", queryBitArray, 3)
        self.assertEquals([("term0", 5), ("term2", 3), ("term4", 1)], result)

    def testBitArrayForQueryResult(self):
        class MockHits(list):
            def getLuceneDocIds(self):
                return self

        mockBitArray = MockBitArray([])
        self._luceneIndex._createBitArray = lambda length, cardinality: mockBitArray

        documents = [10, 11, 12, 1, 2, 3]
        hits = MockHits(documents)
        result = self._luceneIndex._bitArrayForQueryResult(hits)
        self.assertEquals(set(documents), mockBitArray._docs)

    def testSearchUsesUntokenizedFieldsForSort(self):
        #this is not even required, kept for documentation purposes:
        #self._luceneIndex._untokenizedTwinFieldnames = ['sortField']
        queryWrapper = QueryWrapper('titel', sortBy = 'sortField')
        self.assertEquals('sortField__untokenized__', queryWrapper._sortBy)

class MockBitArray:

    def __init__(self, docs):
        self._docs = set(docs)
        self._cardinalityCalled = False
        self._combinedCardinalityCalled = False

    def cardinality(self):
        self._cardinalityCalled = True
        return len(self._docs)

    def combinedCardinality(self, other):
        self._combinedCardinalityCalled = True
        other._combinedCardinalityCalled = True
        return len(self._docs.intersection(other._docs))

    def set(self, position):
        self._docs.add(position)

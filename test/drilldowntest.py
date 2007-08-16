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
from lucenerawdocsetstest import addUntokenized

from meresco.components.lucene.lucene import LuceneIndex
from meresco.components.drilldown.lucenerawdocsets import LuceneRawDocSets
from meresco.components.drilldown.drilldown2 import DrillDown

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

        convertor = LuceneRawDocSets(self._luceneIndex._getReader(), ['field_0', 'field_1'])
        drillDown = DrillDown(['field_0', 'field_1'])
        drillDown.loadDocSets(convertor.getDocSets(), convertor.docCount())

        queryResults = self._luceneIndex.executeQuery(TermQuery(Term("field_1", "inquery")))
        self.assertEquals(3, len(queryResults))

        drilldownResult = list(drillDown.drillDown(queryResults.docNumbers(), [('field_0', 0), ('field_1', 0)]))

        self.assertEquals(2, len(drilldownResult))
        result = dict(drilldownResult)
        self.assertEquals(['field_0', 'field_1'], result.keys())
        self.assertEquals([("this is term_0", 2), ("this is term_1", 1)], list(result['field_0']))
        self.assertEquals([("inquery", 3)], list(result['field_1']))
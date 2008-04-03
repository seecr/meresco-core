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
from meresco.components.lucene import Document, LuceneIndex
from meresco.components.lucene.hits import Hits
from meresco.components.lucene import document
from cq2utils import CallTrace, CQ2TestCase
from timerfortestsupport import TimerForTestSupport

from PyLucene import TermQuery, Term

class HitsTest(CQ2TestCase):

    def testIterator(self):
        iterator = self.createHits(range(3)).__iter__()
        self.assertEquals(["id0", "id1", "id2"], list(iterator))

    def testLen(self):
        hits = self.createHits(range(15))
        self.assertEquals(15, len(hits))

    def testBitMatrixRow(self):
        index = LuceneIndex(self.tempdir, 'cql composer ignored', TimerForTestSupport())
        document = Document('0')
        document.addIndexedField('field', 'value')
        index.addDocument(document)

        document = Document('1')
        document.addIndexedField('field', 'nonMatching')
        index.addDocument(document)

        document = Document('2')
        document.addIndexedField('field', 'value')
        index.addDocument(document)

        hits = index.executeQuery(TermQuery(Term('field', 'value')))
        self.assertEquals([0, 2], list(hits.bitMatrixRow().asList()))


    def testQueryIsExecuted(self):
        hitsCount = 3
        topDocs = MockTopDocs(range(hitsCount))

        aSearcher = CallTrace("Searcher")
        aSearcher.returnValues['search'] = topDocs

        reader = CallTrace('reader', verbose=True)

        aWeight = CallTrace("Weight")

        aQuery = CallTrace("Query")
        aQuery.returnValues['weight'] = aWeight

        Hits(aSearcher, reader, aQuery, None)

        self.assertEquals([
            "weight(<CallTrace: Searcher>)"], aQuery.__calltrace__())

        self.assertEquals([
            "search(<CallTrace: Weight>, None, 10)"], aSearcher.__calltrace__())

    def testQueryIsExecutedWithSort(self):
        hitsCount = 3
        topDocs = MockTopDocs(range(hitsCount))

        aSearcher = CallTrace("Searcher")
        aSearcher.returnValues['search'] = topDocs

        reader = CallTrace('reader')

        aWeight = CallTrace("Weight")

        aQuery = CallTrace("Query")
        aQuery.returnValues['weight'] = aWeight

        aSort = CallTrace("Sort")
        aSort.returnValues['__nonzero__'] = True

        Hits(aSearcher, reader, aQuery, aSort)

        self.assertEquals([
            "weight(<CallTrace: Searcher>)"], aQuery.__calltrace__())

        self.assertEquals([
            "search(<CallTrace: Weight>, None, 10, <CallTrace: Sort>)"], aSearcher.__calltrace__())


    def createHits(self, luceneIds):
        reader = CallTrace()
        aSearcher = MockSearcher(luceneIds, MockTopDocs(luceneIds))
        aQuery = CallTrace("PyLuceneQuery")
        aSort = None
        return Hits(aSearcher, reader, aQuery, aSort)

class MockTopDocs:
    def __init__(self, luceneIds):
        self.scoreDocs = map(MockScoreDoc, luceneIds)
        self.totalHits = len(self.scoreDocs)

class MockScoreDoc:
    def __init__(self, luceneId):
        self.doc = luceneId

class MockSearcher:
    def __init__(self, luceneIds, topDocs):
        self._luceneIds = luceneIds
        self._topDocs = topDocs

    def doc(self, luceneId):
        return MockPyLuceneDocument(luceneId)

    def search(self, weight, filter, nrOrCollector, sort=None):
        if type(nrOrCollector) == int:
            return self._topDocs
        else:
            for id in self._luceneIds:
                nrOrCollector.collect(id, None)


class MockPyLuceneDocument:

    def __init__(self, luceneId):
        self._luceneId = luceneId

    def get(self, fieldname):
        if not fieldname == document.IDFIELD:
            raise Exception("fieldname %s != document.IDFIELD" % fieldname)
        return "id%i" % self._luceneId


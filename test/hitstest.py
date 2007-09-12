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
from meresco.components.lucene import hits
import unittest
from meresco.components.lucene import document
from cq2utils.calltrace import CallTrace

class HitsTest(unittest.TestCase):
    
    def testIterator(self):
        iterator = self.createHits(range(3)).__iter__()
        self.assertEquals(["id0", "id1", "id2"], list(iterator))
        
    def testLen(self):
        hits = self.createHits(range(15))
        self.assertEquals(15, len(hits))
        
    def testDocNumbers(self):
        pyLuceneIds = [33, 34, 10, 11, 12, 54, 55]
        hits = self.createHits(pyLuceneIds)
        self.assertEquals(pyLuceneIds, list(hits.docNumbers()))
    
    def testQueryIsExecuted(self):
        hitsCount = 3
        topDocs = MockTopDocs(range(hitsCount))
        
        aSearcher = CallTrace("Searcher")
        aSearcher.returnValues['search'] = topDocs
        
        aWeight = CallTrace("Weight")
        
        aQuery = CallTrace("Query")
        aQuery.returnValues['weight'] = aWeight
        
        hits.Hits(aSearcher, aQuery, None)
        
        self.assertEquals([
            "weight(<CallTrace: Searcher>)"], aQuery.__calltrace__())
        
        self.assertEquals([
            "search(<CallTrace: Weight>, None, 10)"], aSearcher.__calltrace__())
            
    def testQueryIsExecutedWithSort(self):
        hitsCount = 3
        topDocs = MockTopDocs(range(hitsCount))
        
        aSearcher = CallTrace("Searcher")
        aSearcher.returnValues['search'] = topDocs
        
        aWeight = CallTrace("Weight")
        
        aQuery = CallTrace("Query")
        aQuery.returnValues['weight'] = aWeight
        
        aSort = CallTrace("Sort")
        aSort.returnValues['__nonzero__'] = True
        
        hits.Hits(aSearcher, aQuery, aSort)
        
        self.assertEquals([
            "weight(<CallTrace: Searcher>)"], aQuery.__calltrace__())
        
        self.assertEquals([
            "search(<CallTrace: Weight>, None, 10, <CallTrace: Sort>)"], aSearcher.__calltrace__())
    
        
    def createHits(self, luceneIds):
        aSearcher = MockSearcher(MockTopDocs(luceneIds))
        aQuery = CallTrace("PyLuceneQuery")
        aSort = None
        return hits.Hits(aSearcher, aQuery, aSort)
    
class MockTopDocs:
    def __init__(self, luceneIds):
        self.scoreDocs = map(MockScoreDoc, luceneIds)
        self.totalHits = len(self.scoreDocs)
        
class MockScoreDoc:
    def __init__(self, luceneId):
        self.doc = luceneId
        
class MockSearcher:
    def __init__(self, topDocs):
        self._topDocs = topDocs
    
    def doc(self, luceneId):
        return MockPyLuceneDocument(luceneId)
    
    def search(self, *args):
        return self._topDocs
    
class MockPyLuceneDocument:
    
    def __init__(self, luceneId):
        self._luceneId = luceneId
        
    def get(self, fieldname):
        if not fieldname == document.IDFIELD:
            raise Exception("fieldname %s != document.IDFIELD" % fieldname)
        return "id%i" % self._luceneId
        
if __name__ == "__main__":
    unittest.main()

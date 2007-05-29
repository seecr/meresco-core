from core.index import hits
import unittest
from teddy import document
from cq2utils.calltrace import CallTrace

class HitsTest(unittest.TestCase):
	
	def testIterator(self):
		iterator = self.createHits(range(3)).__iter__()
		self.assertEquals(["id0", "id1", "id2"], list(iterator))
		
	def testSliceOperator(self):
		def check(expected, inputListLength, slice_lo, slice_hi):
			hits = self.createHits(range(inputListLength))
			self.assertEquals(expected, list(hits[slice_lo:slice_hi]))
		
		check([], 100, 10, 10)
		check([], 0, 10, 100)
		check(["id0", "id1"], 100, 0, 2)
		check(["id10", "id11"], 100, 10, 12)
		check(["id10", "id11"], 12, 10, 100)
		#wrapper[-1:]
		check(['id99'], 100, -1, 2**31)
		
	def testLen(self):
		hits = self.createHits(range(15))
		self.assertEquals(15, len(hits))
		
	def testGetLuceneDocIds(self):
		pyLuceneIds = [33, 34, 10, 11, 12, 54, 55]
		hits = self.createHits(pyLuceneIds)
		self.assertEquals(pyLuceneIds, list(hits.getLuceneDocIds()))
	
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
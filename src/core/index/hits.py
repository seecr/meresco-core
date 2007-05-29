from meresco.teddy import document

DEFAULT_FETCHED_DOCS_COUNT = 10

class Hits:
	"""TJ/KVS: we zien in dat deze class nu twee dingen doet (zoekachtige dingen en slicen). Echter, we zijn nog niet in staat geweest het mes netjes te zetten. 2006-08-24"""
		
	def __init__(self, searcher, pyLuceneQuery, pyLuceneSort):
		self._searcher = searcher
		self._pyLuceneQuery = pyLuceneQuery
		self._pyLuceneSort = pyLuceneSort
		
		self._weight = None
		self._scoreDocs = []
		
		self._ensureEnoughScoreDocs(DEFAULT_FETCHED_DOCS_COUNT)
		
	def getLuceneDocIds(self):
		self._ensureEnoughScoreDocs(len(self))
		return [scoreDoc.doc for scoreDoc in self._scoreDocs]
	
	def __len__(self):
		return self._len
	
	def __getslice__(self, i, j):
		j = min(len(self), j)
		self._ensureEnoughScoreDocs(j)
		for hitPosition in xrange(i, j):
			yield self._getTeddyId(hitPosition)
			
	def __iter__(self):
		return self[:]
	
	def _ensureEnoughScoreDocs(self, nrOfDocs):
		if nrOfDocs <= max(len(self._scoreDocs), 1):
			return
		if self._pyLuceneSort:
			topDocs = self._searcher.search(self._getWeight(), None, nrOfDocs, self._pyLuceneSort)
		else:
			topDocs = self._searcher.search(self._getWeight(), None, nrOfDocs)
		self._len = topDocs.totalHits
		self._scoreDocs = topDocs.scoreDocs

	def _getTeddyId(self, hitPosition):
		luceneId = self._scoreDocs[hitPosition].doc
		luceneDoc = self._searcher.doc(luceneId)
		return luceneDoc.get(document.IDFIELD)
			
	def _getWeight(self):
		if self._weight == None:
			self._weight = self._pyLuceneQuery.weight(self._searcher)
		return self._weight

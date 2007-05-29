from meresco.teddy import document
from meresco.core.index.xslice import XSlice

DEFAULT_FETCHED_DOCS_COUNT = 10

class Hits:
	"""Remake of Lucene's hits object, with added 'TeddyIds' functionality
	Provides high performance access to both
		- luceneDocIds (without fetching the associated document
			- Using the special method getLuceneDocIds
		- TeddyIds (the associated document is fetched)
			- These ids are returned for __getitem__, __getslice__ and __iter__
		- __len__ is equal for these two approaches
		
	Implementation hint: the performance benefit is achieved because we know exactly how many documents will be needed. Note the positions of self._loadScoreDocs in the code
	"""
		
	def __init__(self, searcher, pyLuceneQuery, pyLuceneSort):
		self._searcher = searcher
		self._pyLuceneQuery = pyLuceneQuery
		self._pyLuceneSort = pyLuceneSort
		
		#attributes for high-performance remake of PyLucene
		self._weight = None
		self._scoreDocs = []
		self._totalHits = self._loadScoreDocs(DEFAULT_FETCHED_DOCS_COUNT)
		
	def __len__(self):
		return self._totalHits
	
	def getLuceneDocIds(self):
		self._loadScoreDocs(self._totalHits)
		return [scoreDoc.doc for scoreDoc in self._scoreDocs]
	
	def __getslice__(self, start, stop):
		self._loadScoreDocs(min(len(self), stop))
		return XSlice(self)[start:stop]
			
	def __iter__(self):
		return self[:]
	
	def __getitem__(self, i):
		return self._getTeddyId(i)
	
	def _getTeddyId(self, hitPosition):
		luceneId = self._scoreDocs[hitPosition].doc
		luceneDoc = self._searcher.doc(luceneId)
		return luceneDoc.get(document.IDFIELD)
			
	def _loadScoreDocs(self, nrOfDocs):
		"""Loads scoredocs, returns total amount of docs."""
		if nrOfDocs <= max(len(self._scoreDocs), 1):
			return
		if self._pyLuceneSort:
			topDocs = self._searcher.search(self._getWeight(), None, nrOfDocs, self._pyLuceneSort)
		else:
			topDocs = self._searcher.search(self._getWeight(), None, nrOfDocs)
		self._scoreDocs = topDocs.scoreDocs
		return topDocs.totalHits

	def _getWeight(self):
		"""Hocus-pocus PyLucene attribute required for expert/low level access methods - cached locally"""
		if self._weight == None:
			self._weight = self._pyLuceneQuery.weight(self._searcher)
		return self._weight


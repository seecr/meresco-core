from bitmatrix import BitMatrix

class FieldMatrix(object):

	def __init__(self, terms, numDocsInIndex):
		self._matrix = BitMatrix(numDocsInIndex)
		self._row2term = {}
		for term, docIds in terms:
			nr = self._matrix.addRow(docIds)
			self._row2term[nr] = term

	def drilldown(self, docIds = None, maxresults = 0):
		if not docIds:
			for nr, occurences in self._matrix.rowCadinalities():
				yield self._row2term[nr], occurences
		else:
			for nr, occurences in self._matrix.combinedRowCardinalities(docIds, maxresults):
				yield self._row2term[nr], occurences

	# below here is for supporting the old test only
	def __len__(self): return len(self._row2term)

	def __iter__(self):
		class MockBitSet:
			def __init__(self, occurences): self._occurences = occurences
			def cardinality(self): return self._occurences
		for nr, occurences in self._matrix.rowCadinalities():
			yield self._row2term[nr], MockBitSet(occurences)

class DrillDown(object):

	def __init__(self, drilldownFieldnames):
		self._drilldownFieldnames = drilldownFieldnames
		self._fieldMatrices = {}
		# for supporting the old test only
		self._docSets = self._fieldMatrices

	def loadDocSets(self, rawDocSets, docCount):
		for fieldname, terms in rawDocSets:
			self._fieldMatrices[fieldname] = FieldMatrix(terms, docCount)

	def drillDown(self, docIds, drillDownFieldnamesAndMaximumResults):
		queryDocSet = self._docSetForQueryResult(docIds)
		for fieldName, maximumResults in drillDownFieldnamesAndMaximumResults:
			if fieldName not in self._drilldownFieldnames:
				raise DrillDownException("No Docset For Field %s, legal docsets: %s" % (fieldName, self._drilldownFieldnames))
			yield fieldName, self._fieldMatrices[fieldName].drilldown(queryDocSet, maximumResults)

	def _docSetForQueryResult(self, docIds):
		return sorted(docIds) #  <====  What to do about this sorting and performance ?

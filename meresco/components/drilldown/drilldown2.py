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

class Drilldown(object):

	def __init__(self, drilldownFieldnames):
		self._drilldownFieldnames = drilldownFieldnames
		self._fieldMatrices = {}
		# for supporting the old test only
		self._docSets = self._fieldMatrices

	def loadDocSets(self, rawDocSets, docCount):
		for fieldname, terms in rawDocSets:
			self._fieldMatrices[fieldname] = FieldMatrix(terms, docCount)

	def drilldown(self, docIds, drilldownFieldnamesAndMaximumResults):
		queryDocSet = self._docSetForQueryResult(docIds)
		for fieldName, maximumResults in drilldownFieldnamesAndMaximumResults:
			if fieldName not in self._drilldownFieldnames:
				raise DrilldownException("No Docset For Field %s, legal docsets: %s" % (fieldName, self._drilldownFieldnames))
			yield fieldName, self._fieldMatrices[fieldName].drilldown(queryDocSet, maximumResults)

	def _docSetForQueryResult(self, docIds):
		return sorted(docIds) #  <====  What to do about this sorting and performance ?

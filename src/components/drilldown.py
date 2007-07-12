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

DENSE_SPARSE_BREAKING_POINT = 32

class DocSet:
	
	def __init__(self, docs, length):
		cardinality = len(docs)
		if cardinality * DENSE_SPARSE_BREAKING_POINT > length:
			result = DenseBitArray(length)
		result = SparseBitArray(cardinality)
		for doc in docs:
			result.set(doc)
		return result
	
class DrillDown:
	
	def __init__(self, index, drillDownFieldNames):
		self._index = index
		self._drillDownFieldnames = drillDownFieldNames

	def _totalDocsInIndex(self):
		return self._getReader().numDocs()
	
	def process(self, hits, drillDownFieldnamesAndMaximumResults):
		drillDownResults = []
		queryDocSet = self._docSetForQueryResult(hits)
		for (fieldName, maximumResults) in drillDownFieldnamesAndMaximumResults:
			drillDownResults.append((fieldName,
					self._countField(fieldName, queryDocSet, maximumResults)))
		return drillDownResults
	
	def _docSetForQueryResult(self, hits):
		sortedDocs = hits.getLuceneDocIds()
		sortedDocs.sort()
		return DocSet(hits, self._totalDocsInIndex())
	
	def _reloadDocSets(self):
		self._docSets = {}
		for fieldName in self._drillDownFieldnames:
			self._docSets[fieldName] = self._docSetsForField(fieldName + "__untokenized__")

	def _docSetsForField(self, fieldName):
		reader = self._getReader()
		
		result = []
		termDocs = reader.termDocs()
		termEnum = reader.terms(PyLucene.Term(fieldName, ''))
		#reader.terms returns something of the following form, if fieldname == fieldname3
		#fieldname3 'abla'
		#fieldname3 'bb'
		#fieldname3 'zz'
		#fieldname4 'aa'
		
		#The enum has the following (weird) behaviour: the internal pointer references
		#the first element by default, but when there are no elements it references a
		#None element. Therefor we have to check "if not term".
		#We use a "do ... while" idiom because calling next would advance the internal
		#pointer, resulting in a missed first element
		
		while True:
			term = termEnum.term()
			if not term or term.field() != fieldName:
				break
			
			termDocs.seek(term)
			
			docs = []
			while termDocs.next():
				docs.append(termDocs.doc())
			docSet = DocSet(docs, self._totalDocsInIndex())
			
			result.append((term.text(), docSet))
			
			if not termEnum.next():
				break
		
		def cmpDescCardinaltiy((term1, docSet1), (term2, docSet2)):
			return docSet2.cardinality() - docSet1.cardinality()
		
		result.sort(cmpDescCardinaltiy)
		return result
			
	def _countField(self, fieldName, drillDownBitArray = None, maximumResults = 0):
		
		#sort on cardinality, truncate with maximumResults and return smallest cardinality
		#if no limit is present return 0
		def sortAndTruncateAndGetMinValueInResult(resultList):
			if maximumResults:
				resultList.sort(lambda (termL, countL), (termR, countR): cmp(countR, countL))
				del resultList[maximumResults:]
				if len(resultList) == maximumResults:
					return resultList[-1][1] #Cardinality of last element
			return 0

		if not self._bitArrays.has_key(fieldName):
			raise LuceneException("No BitArray for field " + fieldName)
		result = []
		
		if not drillDownBitArray:
			for term, bitarray in self._bitArrays[fieldName]:
				result.append((term, bitarray.cardinality()))
		else: #Use drillDownBitArray
			minValueInResult = 0
			for term, bitarray in self._bitArrays[fieldName]:
				if bitarray.cardinality() < minValueInResult:
					break

				cardinality = bitarray.combinedCardinality(drillDownBitArray)
								
				if cardinality > minValueInResult:
					result.append((term, cardinality))
					minValueInResult = sortAndTruncateAndGetMinValueInResult(result)
		return result
				
	#FROM teddyquery.py (Teddy 2.x) - probably not required.
	def drillDown(self, callback):
		if not self._hitsWrapper:
			raise Exception("TeddyQuery.drillDown called before query")
		result = 0
		if self._drillDownFields:
			result = self.duration(self._drillDownCore)
			self._logging and self._logline.set('drilldownDuration', result)
			for fieldname, tuples in self._drillDownResults.items():
				callback(fieldname, tuples)
		return result
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

import PyLucene
from meresco.components.drilldown.cpp.bitarray import DenseBitArray, SparseBitArray

DENSE_SPARSE_BREAKING_POINT = 32

def createDocSet(docs, length):
	cardinality = len(docs)
	if cardinality * DENSE_SPARSE_BREAKING_POINT > length:
		result = DenseBitArray(length)
	result = SparseBitArray(cardinality)
	for doc in docs:
		result.set(doc)
	return result
	
class DrillDown:
	
	def __init__(self, luceneIndexReader, drillDownFieldNames):
		self._reader = luceneIndexReader
		
		self._drillDownFieldnames = drillDownFieldNames

	def _numDocsInIndex(self):
		return self._reader.numDocs()
	
	def process(self, docIds, drillDownFieldnamesAndMaximumResults):
		drillDownResults = []
		queryDocSet = self._docSetForQueryResult(docIds)
		for (fieldName, maximumResults) in drillDownFieldnamesAndMaximumResults:
			drillDownResults.append((fieldName,
					self._processField(fieldName, queryDocSet, maximumResults)))
		return drillDownResults
	
	def _docSetForQueryResult(self, docIds):
		sortedDocs = docIds
		sortedDocs.sort()
		return createDocSet(docIds, self._numDocsInIndex())
	
	def reloadDocSets(self):
		self._docSets = {}
		for fieldName in self._drillDownFieldnames:
			self._docSets[fieldName] = self._docSetsForField(fieldName + "__untokenized__")

	def _docSetsForFieldLucene(self, fieldName):
		print "Warrrrring" # - de controlflow is hier wat te refactoren, zodat echt alleen de lucene stukjes hieronder vallen"
		result = []
		termDocs = self._reader.termDocs()
		termEnum = self._reader.terms(PyLucene.Term(fieldName, ''))
		#IndexReader.terms returns something of the following form, if fieldname == fieldname3
		#fieldname3 'abla'
		#fieldname3 'bb'
		#fielname3 'zz'
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
			docSet = createDocSet(docs, self._numDocsInIndex())
			
			result.append((term.text(), docSet))
			if not termEnum.next():
				break
			
		return result
		
	def _docSetsForField(self, fieldName):
		result = self._docSetsForFieldLucene(fieldName)
		def cmpDescCardinality((term1, docSet1), (term2, docSet2)):
			return docSet2.cardinality() - docSet1.cardinality()
		
		result.sort(cmpDescCardinality)
		return result
			
	def _processField(self, fieldName, drillDownBitArray = None, maximumResults = 0):
		
		#sort on cardinality, truncate with maximumResults and return smallest cardinality
		#if no limit is present return 0
		def sortAndTruncateAndGetMinValueInResult(resultList):
			if maximumResults:
				resultList.sort(lambda (termL, countL), (termR, countR): cmp(countR, countL))
				del resultList[maximumResults:]
				if len(resultList) == maximumResults:
					return resultList[-1][1] #Cardinality of last element
			return 0

		if not self._docSets.has_key(fieldName):
			raise LuceneException("No Docset For Field " + fieldName)
		result = []
		
		if not drillDownBitArray:
			for term, docSet in self._docSets[fieldName]:
				result.append((term, docSet.cardinality()))
		else: #Use drillDownBitArray
			minValueInResult = 0
			for term, docSet in self._docSets[fieldName]:
				if docSet.cardinality() < minValueInResult:
					break

				cardinality = docSet.combinedCardinality(drillDownBitArray)
								
				if cardinality > minValueInResult:
					result.append((term, cardinality))
					minValueInResult = sortAndTruncateAndGetMinValueInResult(result)
		return result

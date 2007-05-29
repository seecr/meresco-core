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
#
# Lucene
#

import os
import PyLucene
import xml.sax.saxutils
from document import IDFIELD, CONTENTFIELD
from meresco.core.index.hits import Hits

DEFAULT_OFFSET = 0
DEFAULT_COUNT = 10

class LuceneException(Exception):
	pass

class LuceneQuery:
	def __init__(self, aLuceneIndex, aQueryString, anOffset = DEFAULT_OFFSET, 
				aCount = DEFAULT_COUNT, sortBy = None, sortDescending = None):
		self._index = aLuceneIndex
		self._offset = anOffset
		self._count = aCount
		self._queryString = aQueryString
		self._hitCount = 0
		self._batchSize = 0
		self._sortBy = sortBy
		self._sortDescending = sortDescending
		analyzer = PyLucene.StandardAnalyzer()
		queryParser = PyLucene.QueryParser(CONTENTFIELD, analyzer)
		queryParser.setDefaultOperator(PyLucene.QueryParser.Operator.AND)
		self._query = queryParser.parse(self._queryString)

	def perform(self):
		hits = self._index.search(self._getQuery(), self._getSort())
		self._hitCount = hits.length()
		batch = range(self._offset, min(self._offset + self._count, self._hitCount))
		for h in batch:
			yield hits.doc(h).get(IDFIELD)
		self._batchSize = len(batch)

	def getBatchSize(self):
		return self._batchSize

	def getOffset(self):
		return self._offset
	
	def getCount(self):
		return self._count

	def getHitCount(self):
		return self._hitCount

	def _getSort(self):
		sortDir = bool(self._sortDescending)
		return self._sortBy and \
			PyLucene.Sort(self._sortBy, sortDir) or None

	def _getQuery(self):
		return self._query

class LuceneIndex:
	
	def __init__(self, aDirectoryName):
		self._searcher = None
		self._reader = None
		
		self._directoryName = aDirectoryName
		if not os.path.isdir(self._directoryName):
			os.makedirs(self._directoryName)
				
		if not self._indexExists():
			self._createIndex()
			
		self.reOpen()
		self._indexChanged = False
			
	def _createIndex(self):
		self._getWriter(createIndex = True).close()
		
	def reOpen(self):
		if self._searcher != None:
			self._searcher.close()
		self._searcher = PyLucene.IndexSearcher(self._directoryName)
	
	def createQuery(self, aString, anOffset = DEFAULT_OFFSET, aCount = DEFAULT_COUNT, sortBy = None, sortDescending = False):
		return LuceneQuery(self, aString, anOffset, aCount, sortBy, sortDescending)
	
	#TODO needs test (probably just test method calls)
	def executeQuery(self, aQueryWrapper):
		return Hits(self._searcher, aQueryWrapper.getPyLuceneQuery(), aQueryWrapper.getPyLuceneSort())

	def search(self, query, sort):
		search = self._getSearch()
		return sort and search.search(query, sort) or search.search(query)

	def addToIndex(self, aDocument):
		aDocument.validate()
		
		writer = self._getWriter()
		try:
			aDocument.addToIndexWith(writer)
		finally:
			writer.close()
			self._indexChanged = True

	def optimize(self):
		if self._reader:
			self._reader.close()
			
		writer = self._getWriter()
		try:
			writer.optimize()
		finally:
			writer.close()
			
	def __del__(self):
		if self._indexChanged:
			self.optimize()
		
	def _getWriter(self, createIndex = False):
		self._closeReader()
		analyzer = PyLucene.StandardAnalyzer()
		return PyLucene.IndexWriter(self._directoryName, analyzer, createIndex)
		
	def _getSearch(self):
		if self._searcher == None:
			self.reOpen()
		return self._searcher
	
	def _closeReader(self):
		if self._reader:
			self._reader.close()
			self._reader = None

	def _getReader(self):
		if not self._reader:
			self._reader = PyLucene.IndexReader.open(self._directoryName)
		return self._reader
	
	def _indexExists(self):
		return PyLucene.IndexReader.indexExists(self._directoryName)
	
	def deleteID(self, anId):
		reader = self._getReader()
		reader.deleteDocuments(PyLucene.Term(IDFIELD, anId))
		self._closeReader()

	def queryWith(self, aLuceneQuery):
		if not self._indexExists:
			raise LuceneException('Index does not exist')
		for hit in aLuceneQuery.search():
			yield hit
	
	def query(self, aQuery):
		return self._getSearch().search(aQuery)

	def countField(self, fieldName):
		reader = self._getReader()
		search = self._getSearch()
		countDict = {}
		try:
	
			termEnum = reader.terms(PyLucene.Term(fieldName, ''))
			termIter = TermIter(termEnum, fieldName)
			
			for term in termIter:
				countDict[term.text()] = reader.docFreq(term)
	
			return countDict.items()
		finally:
			self._closeReader()
		
	def updateField(self, anId, fieldName, value):
		pass
		
class TermIter:
	def __init__(self, termEnum, fieldName):
		self._termEnum = termEnum
		self._nextTerm = termEnum.term()
		self._fieldName = fieldName
	
	def __iter__(self):
		return self
	
	def next(self):
		if self._nextTerm == None or self._nextTerm.field() != self._fieldName:
			raise StopIteration()
		result, self._nextTerm = self._nextTerm, None
		if self._termEnum.next():
			self._nextTerm = self._termEnum.term()
		return result

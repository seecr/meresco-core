## begin license ##
#
#    Teddy is the name for Seek You Too's Search Appliance.
#    Copyright (C) 2006 Stichting SURF. http://www.surf.nl
#    Copyright (C) 2006-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of Teddy.
#
#    Teddy is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Teddy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Teddy; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
from queryserver.plugins.searchinterface import SearchInterface, SearchResult, SearchRecord
from cqlparser.lucenecomposer import fromString as cqlToLucene
from storage.storage import StorageException
from cStringIO import StringIO

SRU_IS_ONE_BASED = 1
		
class TeddyInterface(SearchInterface):
	"""
	Interface used by queryserver to query a search engine.
	"""
	def __init__(self, luceneIndex, storage):
		self._luceneIndex = luceneIndex
		self._storage = storage
	
	def search(self, sruQuery):
		"""
		Perform a query using the parameters specified in the sru query and return a SearchResult object representing the results of the query.
		"""
		luceneQueryString = cqlToLucene(sruQuery.query)
		offset = sruQuery.startRecord - SRU_IS_ONE_BASED
		batchSize = sruQuery.maximumRecords
		sortBy = sruQuery.sortBy
		sortDescending = sruQuery.sortDirection
		luceneQuery = self._luceneIndex.createQuery(
			luceneQueryString,
			offset,
			batchSize, 
			sortBy, 
			sortDescending)
		return TeddyResult(luceneQuery, self._storage)
	
	def countField(self, fieldName):
		"""
		Special method to count the number of occurrences of a given field.
		This method does not belong to the default SearchInterface
		"""
		return self._luceneIndex.countField(fieldName)
	
	def reset(self):
		self._luceneIndex.reOpen()
	
class TeddyResult(SearchResult):
	"""
	Abstract class that defines methods needed for the queryserver to generate its output
	"""
	def __init__(self, luceneQuery, storage):
		self._luceneQuery = luceneQuery
		self._storage = storage
	
	def getNumberOfRecords(self):
		"""
		Return the total number of records in the result
		Number Of Records are only available after all records have been written.
		"""
		return 0
	
	def getRecords(self):
		"""
		Return a generator that will yield one SearchRecord object at a time
		"""
		return (TeddyRecord(documentId, self._storage) for documentId in self._luceneQuery.perform())
	
	def getNextRecordPosition(self):
		"""
		Returns the recordPosition for the next batch.
		Returns None if no more records available.
		"""
		nextPosition = self._luceneQuery.getOffset() + self._luceneQuery.getCount() + SRU_IS_ONE_BASED
		return nextPosition < self._luceneQuery.getHitCount() and nextPosition or None
	
	def writeExtraResponseDataOn(self, aStream):
		"""
		Write, if any, extra data that is available to the given stream
		"""
		aStream.write('<numberOfRecords>%d</numberOfRecords>' % self._luceneQuery.getHitCount())
	
class TeddyRecord(SearchRecord):
	def __init__(self, documentId, storage):
		self._documentId = documentId
		self._storage = storage
	
	def _getStorageUnit(self):
		return self._storage.getUnit(self._documentId)

	def writeDataOn(self, dataName, aStream):
		"""
		Write data with name to aStream
		
		JJ: Evil code! If there is an inconsistency between the index and the storage, then it is possible for the storage being asked to retrieve a document that does not exist. This leads to an StorageException which currently floats up to the SRU interface generating an Diagnostics. This messes up the SRU response. Therefor it now writes an empty record to indicate something went wrong. There will need to be a better solution implemented for this, but currently that is not within the scope of this task.
		"""
		box = self.readData(dataName)
		try:
			for stuff in box:
				aStream.write(stuff)
		finally:
			box.close()
				
	def readData(self, dataName):
		try:
			return self._getStorageUnit().openBox(dataName)
		except (IOError, StorageException):
			return StringIO()
		
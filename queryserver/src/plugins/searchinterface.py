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


class SearchInterface:
	"""
	Interface used by queryserver to query a search engine.
	"""
	def search(self, sruQuery):
		"""
		Perform a query using the parameters specified in the sru query and return a SearchResult object representing the results of the query.
		"""
		raise NotImplementedError()
	
	def reset(self):
		"""
		Reset the searchInterface, might be necessary after updates.
		"""
		raise NotImplementedError()
	
class SearchResult:
	"""
	Abstract class that defines methods needed for the queryserver to generate its output
	"""
	
	def getNumberOfRecords(self):
		"""
		Return the total number of records in the result
		"""
		raise NotImplementedError()
	
	def getRecords(self):
		"""
		Return a generator that will yield one SearchRecord object at a time
		"""
		raise NotImplementedError()
	
	def getNextRecordPosition(self):
		"""
		Returns the recordPosition for the next batch.
		Returns None if no more records available.
		"""
		raise NotImplementedError()
	
	def writeExtraResponseDataOn(self, aStream):
		"""
		Write, if any, extra data that is available to the given stream
		"""
		raise NotImplementedError()
	
class SearchRecord:
	def writeDataOn(self, recordSchema, aStream):
		"""
		Write the recordData with the given schema onto the given stream
		"""
		raise NotImplementedError()
		

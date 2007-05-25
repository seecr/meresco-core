## begin license ##
#
#    QueryServer is a framework for handling search queries.
#    Copyright (C) 2005-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of QueryServer.
#
#    QueryServer is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    QueryServer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with QueryServer; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from cqlparser import parseString, CQLParseException

class SRUQueryException(Exception):
	pass

class SRUQueryParameterException(SRUQueryException):
	pass

class SRUQueryParseException(SRUQueryException):
	pass

DEFAULT_RECORDSCHEMA = 'dc'

class SRUQuery:
	def __init__(self, database, arguments):
		self.database = database
		self._setupQuery(arguments)

	def _setupQuery(self, arguments):
		startRecord = arguments.get('startRecord', ['1'])[0]
		if not startRecord.isdigit() or int(startRecord) < 1:
			raise SRUQueryParameterException('startRecord')
		self.startRecord = int(startRecord)

		maximumRecords = arguments.get('maximumRecords', ['10'])[0]
		if not maximumRecords.isdigit() or int(maximumRecords) < 1:
			raise SRUQueryParameterException('maximumRecords')
		self.maximumRecords = int(maximumRecords)

		query = arguments.get('query', [''])[0]
		try:
			parseString(query)
		except CQLParseException, e:
			raise SRUQueryParseException(e)
		self.query = query
		
		sortKeys = arguments.get('sortKeys', [''])[0]
		self.sortBy, self.sortDirection = self._parseSort(sortKeys)
		
		self.recordSchema = arguments.get('recordSchema', [DEFAULT_RECORDSCHEMA])[0]
		if self.recordSchema == '':
			self.recordSchema = DEFAULT_RECORDSCHEMA
			
		self.x_recordSchema = filter(str.strip, arguments.get('x-recordSchema', []))
		
		self.recordPacking = 'xml'
		
	def _parseSort(self, sortKeys):
		try:
			sortBy, ignored, sortDirection = sortKeys.split(',')
			return sortBy.strip(), bool(int(sortDirection))
		except ValueError:
			return None, None

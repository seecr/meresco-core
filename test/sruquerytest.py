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

from unittest import TestCase

from meresco.queryserver.plugins.sruquery import SRUQuery, SRUQueryParameterException, SRUQueryParseException

class SRUQueryTest(TestCase):
	def testSortingArgument(self):
		self.assertSortKey('date', False, ['date,,0'])
		self.assertSortKey('date', True, ['date,,1'])
		self.assertSortKey('date', True, ['date,crap,1'])
		self.assertSortKey(None, None, ['crap,crap'])
		self.assertSortKey(None, None, ['crap,crap,,,,,,,,,,,,'])
		self.assertSortKey(None, None, ['date,crap,noInteger'])
		self.assertSortKey(None, None, [''])
		

	def assertSortKey(self, expectedSortBy, expectedSortDirection, sortKeys):
		query = SRUQuery('database', {'query':[''], 'sortKeys':sortKeys})
		self.assertEquals(expectedSortBy, query.sortBy)
		self.assertEquals(expectedSortDirection, query.sortDirection)
		
	def testValidateStartRecord(self):
		try:
			query = SRUQuery('database', {'startRecord':['-1']})
			self.fail()
		except SRUQueryParameterException, e:
			self.assertEquals("startRecord", str(e))
		query = SRUQuery('database', {'startRecord':['8']})
		self.assertEqual(8, query.startRecord)
		
	def testValidateMaximumRecords(self):
		try:
			query = SRUQuery('database', {'maximumRecords':['-1']})
			self.fail()
		except SRUQueryParameterException, e:
			self.assertEquals("maximumRecords", str(e))
		query = SRUQuery('database', {'maximumRecords':['80']})
		self.assertEqual(80, query.maximumRecords)
			
	def testValidateQuery(self):
		try:
			query = SRUQuery('database', {'query':['TERM1)']})
			self.fail()
		except SRUQueryParseException, e:
			self.assertEquals("Unexpected token after parsing, check for greediness ([)], cqlparser.cqlparser.CQL_QUERY(cqlparser.cqlparser.SCOPED_CLAUSE(cqlparser.cqlparser.SEARCH_CLAUSE(cqlparser.cqlparser.SEARCH_TERM('TERM1'))))).", str(e))

	def testRecordSchema(self):
		query = SRUQuery('database', {})
		self.assertEquals('dc', query.recordSchema)

		query = SRUQuery('database', {'recordSchema':['']})
		self.assertEquals('dc', query.recordSchema)

		query = SRUQuery('database', {'recordSchema':['lom']})
		self.assertEquals('lom', query.recordSchema)
		
	def testExtraRecordSchema(self):
		query = SRUQuery('database', {})
		self.assertEquals([], query.x_recordSchema)

		query = SRUQuery('database', {'x-recordSchema':['']})
		self.assertEquals([], query.x_recordSchema)

		query = SRUQuery('database', {'x-recordSchema':['lom']})
		self.assertEquals(['lom'], query.x_recordSchema)
		
		query = SRUQuery('database', {'x-recordSchema':['lom', 'fields']})
		self.assertEquals(['lom', 'fields'], query.x_recordSchema)

		query = SRUQuery('database', {'x-recordSchema':['lom', '', 'fields']})
		self.assertEquals(['lom', 'fields'], query.x_recordSchema)

	def testRecordPacking(self):
		query = SRUQuery('database', {})
		self.assertEquals('xml', query.recordPacking)

		query = SRUQuery('database', {'recordPacking': ['string']})
		#ignored
		self.assertEquals('xml', query.recordPacking)


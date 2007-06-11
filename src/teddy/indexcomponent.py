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

from cq2utils.component import Component
from amara import binderytools
from xml.sax import SAXParseException
from meresco.core.index.querywrapper import QueryWrapper
from PyLucene import BooleanQuery, BooleanQuery, BooleanClause, RangeQuery, Term, TermQuery, MatchAllDocsQuery
from meresco.queryserver.observers.stampcomponent import STAMP_PART, DATESTAMP, UNIQUE
from meresco.queryserver.observers.partscomponent import PARTS_PART, PART
from meresco.queryserver.observers.setscomponent import SETS_PART, SET

LO = '0' #sorts lower/eq than all numbers (as strings)
HI = 'A' #sorts higher than all numbers (as strings)

class IndexComponent(Component):
	def __init__(self, anIndex):
		self._index = anIndex
		
	def delete(self, notification):
		self._index.deleteID(notification.id)
		
	def add(self, notification):
		self._index.deleteID(notification.id)
		self._index.addToIndex(notification.document)
			
	def listRecords(self, partName, continueAt = '0', oaiFrom = None, oaiUntil = None, oaiSet = None, sorted = True):
		def addRange(root, field, lo, hi, inclusive):
			range = RangeQuery(Term(field, lo), Term(field, hi), inclusive)
			root.add(range, BooleanClause.Occur.MUST)
		
		#It is necessery here to work with the elematal objects, because the query parser transforms everything into lowercase
		
		query = BooleanQuery()
		query.add(TermQuery(Term('%s.%s' % (PARTS_PART, PART), partName)), BooleanClause.Occur.MUST)
		if continueAt != '0':	
			addRange(query, '%s.%s' % (STAMP_PART, UNIQUE), continueAt, HI, False)
		if oaiFrom or oaiUntil:
			oaiFrom = oaiFrom or LO
			oaiUntil = oaiUntil or HI
			addRange(query, '%s.%s' % (STAMP_PART, DATESTAMP), oaiFrom, oaiUntil, True)
		if oaiSet:
			query.add(TermQuery(Term('%s.%s' % (SETS_PART, SET), oaiSet)), BooleanClause.Occur.MUST)

		sortBy = sorted and '%s.%s' % (STAMP_PART, UNIQUE)
		
		return self._index.executeQuery(QueryWrapper(query, sortBy))

	def listAll(self):
		return self._index.executeQuery(QueryWrapper(MatchAllDocsQuery(), None))

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
from meresco.components.lucene import document

class QueryWrapper:
	
	def __init__(self, pyLuceneQuery, sortBy = None, sortDescending = None):
		self._sortBy = sortBy
		self._sortDescending = sortDescending
		self._pyLuceneQuery = pyLuceneQuery

	def getPyLuceneQuery(self):
		return self._pyLuceneQuery
	
	def getPyLuceneSort(self):
		return self._sortBy and	PyLucene.Sort(self._sortBy, bool(self._sortDescending)) or None

class AdvancedQueryWrapper(QueryWrapper):
	"""QueryWrapper wraps a PyLucene query
	- It has functionality for parsing and sorting
	- It has intelligence about the "teddy approach" - i.e. defaulting to __content__ field
	
	in Teddy 2.0 (commented out): knowledge about __untokenized__ fields (sorting)
	"""
		
	def __init__(self, queryString, sortBy = None, sortDescending = None):
		#TEDDY2.0: , untokenizedFieldNames = []):
		self._queryString = queryString
		self._sortBy = sortBy #TEDDY2.0: and sortBy + '__untokenized__' or sortBy
		self._sortDescending = sortDescending
		
		analyzer = PyLucene.StandardAnalyzer()
		#TEDDY2.0: analyzer = PyLucene.PerFieldAnalyzerWrapper(analyzer)
		#TEDDY2.0: analyzer.addAnalyzer(document.IDFIELD, PyLucene.KeywordAnalyzer())
		#TEDDY2.0:for fieldName in untokenizedFieldNames:
		#TEDDY2.0:	analyzer.addAnalyzer(fieldName, PyLucene.KeywordAnalyzer())
		
		queryParser = PyLucene.QueryParser(document.CONTENTFIELD, analyzer)
		queryParser.setDefaultOperator(PyLucene.QueryParser.Operator.AND)
		self._pyLuceneQuery = queryParser.parse(self._queryString)

	def getPyLuceneQuery(self):
		return self._pyLuceneQuery
	
	def getPyLuceneSort(self):
		return self._sortBy and	PyLucene.Sort(self._sortBy, bool(self._sortDescending)) or None

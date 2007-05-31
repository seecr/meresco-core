import PyLucene
from meresco.teddy import document

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
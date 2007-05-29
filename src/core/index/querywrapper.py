import PyLucene
import teddy.document

class QueryWrapper:
		
	def __init__(self, queryString, sortBy = None, sortDescending = None, untokenizedFieldNames = []):
		self._queryString = queryString
		self._sortBy = sortBy and sortBy + '__untokenized__' or sortBy
		self._sortDescending = sortDescending
		
		analyzer = PyLucene.StandardAnalyzer()
		analyzer = PyLucene.PerFieldAnalyzerWrapper(analyzer)
		
		analyzer.addAnalyzer(document.IDFIELD, PyLucene.KeywordAnalyzer())
		for fieldName in untokenizedFieldNames:
			analyzer.addAnalyzer(fieldName, PyLucene.KeywordAnalyzer())
		
		queryParser = PyLucene.QueryParser(document.CONTENTFIELD, analyzer)
		queryParser.setDefaultOperator(PyLucene.QueryParser.Operator.AND)
		self._pyLuceneQuery = queryParser.parse(self._queryString)

	def getPyLuceneQuery(self):
		return self._pyLuceneQuery
	
	def getPyLuceneSort(self):
		return self._sortBy and	PyLucene.Sort(self._sortBy, bool(self._sortDescending)) or None
	
#class TermQueryWrapper:
	
	#def __init__(self, field, value):
		#self._pyLuceneQuery = PyLucene.TermQuery(PyLucene.Term(field, value))
		#self._sortBy = None
		#self._sortDescending = None
		
	#def getPyLuceneQuery(self):
		#return self._pyLuceneQuery
	
	#def getPyLuceneSort(self):
		#return None
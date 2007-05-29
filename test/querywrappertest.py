import unittest
from core.index.querywrapper import QueryWrapper

class QueryWrapperTest(unittest.TestCase):
	
	def testDefaultBehavior(self):
		queryWrapper = QueryWrapper('field:value')
		self.assertEquals("field:value", str(queryWrapper.getPyLuceneQuery()))
		queryWrapper = QueryWrapper('value')
		self.assertEquals("__content__:value", str(queryWrapper.getPyLuceneQuery()))
	
	def testDefaultOperatorIsAND(self):
		queryWrapper = QueryWrapper('one two')
		pyLuceneQuery = queryWrapper.getPyLuceneQuery()
		self.assertTrue(pyLuceneQuery.isBooleanQuery())
		self.assertTrue("+" in str(pyLuceneQuery))
	
	def testUntokenizedQuery(self):
		pass
		#TEDDY2.0: recreate this test
		

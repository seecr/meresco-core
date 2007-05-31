import unittest
from core.index.querywrapper import AdvancedQueryWrapper

class QueryWrapperTest(unittest.TestCase):
	
	def testDefaultBehavior(self):
		queryWrapper = AdvancedQueryWrapper('field:value')
		self.assertEquals("field:value", str(queryWrapper.getPyLuceneQuery()))
		queryWrapper = AdvancedQueryWrapper('value')
		self.assertEquals("__content__:value", str(queryWrapper.getPyLuceneQuery()))
	
	def testDefaultOperatorIsAND(self):
		queryWrapper = AdvancedQueryWrapper('one two')
		pyLuceneQuery = queryWrapper.getPyLuceneQuery()
		self.assertTrue(pyLuceneQuery.isBooleanQuery())
		self.assertTrue("+" in str(pyLuceneQuery))
	
	def testUntokenizedQuery(self):
		pass
		#TEDDY2.0: recreate this test
		

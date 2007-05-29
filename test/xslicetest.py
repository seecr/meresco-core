from core.index.xslice import XSlice
import unittest
from teddy import document
from cq2utils.calltrace import CallTrace

class XSliceTest(unittest.TestCase):
	
	def testFunctionality(self):
		self.assertEquals([], list(XSlice(range(100))[10: 10]))
		self.assertEquals([], list(XSlice([])[10: 100]))
		self.assertEquals([0, 1], list(XSlice(range(100))[0: 2]))
		self.assertEquals([10, 11], list(XSlice(range(100))[10: 12]))
		self.assertEquals([10, 11], list(XSlice(range(12))[10: 100]))
		self.assertEquals([99], list(XSlice(range(100))[-1:]))
		
	def testLen(self):
		self.assertEquals(15, len(XSlice(range(15))))
		
	def testNoNeedlessCopying(self):
		class SomeList:
			def __getitem__(self, i):
				requestedItems.append(i)
				return i
				
			def __getslice__(self, lo, hi):
				result = []
				for i in range(lo, hi):
					result.append(self[i])
				return result
		
		#without xSlice:
		requestedItems = []
		conventionalSlice = SomeList()[0:10]
		self.assertEquals(range(10), requestedItems)
		
		#with xSlice:
		requestedItems = []
		xSlice = XSlice(SomeList())[0:10]
		self.assertEquals([], requestedItems)
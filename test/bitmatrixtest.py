from unittest import TestCase
from time import time
from random import random

from meresco.components.drilldown.bitmatrix import BitMatrix

class BitMatrixTest(TestCase):
	def testAdd(self):
		m = BitMatrix()
		n = m.addRow(range(10))
		self.assertEquals(0, n)
		self.assertEquals([(0, 10)], m.rowCadinalities())
		n= m.addRow([1,3,5,8,18])
		self.assertEquals(1, n)
		self.assertEquals([(0, 10), (1, 5)], m.rowCadinalities())

	def testDrilldown(self):
		m = BitMatrix()
		m.addRow(range(10))
		m.addRow([1, 3, 5, 8, 18])
		result = m.combinedRowCardinalities(range(4))
		self.assertEquals((0, 4), result[0])
		self.assertEquals((1, 2), result[1])

	def testMaxResults(self):
		pass

	def testPerformanceOfExtremelyWorstCaseNamelyRandomBits(self):
		print 'Populating matrix, please wait...'
		m = BitMatrix()
		docs = 10000
		terms = 300
		for i in range(terms):
			m.addRow([n for n in range(docs) if int(random()+0.5)])
			#print i

		print 'Executing combinedRowCardinalities(...), please wait...'
		docset = [i for i in range(docs) if int(random()+0.5)]
		start = time()
		for i in range(100):
			m.combinedRowCardinalities(docset)
		t = time() - start
		print '==>', t/100
		#computer,	implementation,	time
		#1.5 GHz Centrino,	Pyrex pure Python without list comprehensions, 275ms
		#1.5 GHz Centrino,	pure Python with list comprehensions,	250ms
		#1.5 GHz Centrino,	pure Python without list comprehensions,	250ms

## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) 2007 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2007 Stichting Kennisnet Ict op school. 
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
from time import time
from random import random

from meresco.components.drilldown.bitmatrix import BitMatrix

class BitMatrixTest(TestCase):

	def testEmpty(self):
		m = BitMatrix()
		c = m.combinedRowCardinalities([])
		self.assertEquals([], c)
		c = m.rowCadinalities()
		self.assertEquals([], c)

	def testEmptyDoc(self):
		m = BitMatrix()
		n = m.addRow([])
		c = m.combinedRowCardinalities([1])
		self.assertEquals([], c)

	def testNoResultLeft(self):
		m = BitMatrix()
		n = m.addRow([1])
		c = m.combinedRowCardinalities([2])
		self.assertEquals([], c)

	def testNoResultRight(self):
		m = BitMatrix()
		n = m.addRow([2])
		c = m.combinedRowCardinalities([1])
		self.assertEquals([], c)

	def testAdd(self):
		m = BitMatrix()
		n = m.addRow([0,2,4,6,8])
		self.assertEquals(0, n)
		n= m.addRow([1,3,5,7,9])
		self.assertEquals(1, n)

	def testRowCardinalities(self):
		m = BitMatrix()
		n = m.addRow([0,2,4,6,8])
		n= m.addRow([1,3,5,7,9])
		self.assertEquals([(0, 5), (1, 5)], m.rowCadinalities())

	def testCombinedRowCardinalitiesOfOne(self):
		m = BitMatrix()
		n = m.addRow([0])
		n= m.addRow([1])
		self.assertEquals([(0, 1), (1, 1)], m.combinedRowCardinalities([0, 1]))
		self.assertEquals([(0, 1)], m.combinedRowCardinalities([0]))
		self.assertEquals([(1, 1)], m.combinedRowCardinalities([1]))

	def testCombinedRowCardinalitiesOfTwo(self):
		m = BitMatrix()
		n = m.addRow([0, 2])
		n= m.addRow([1, 3])
		self.assertEquals([(0, 2)], m.combinedRowCardinalities([0, 2]))
		self.assertEquals([(1, 2)], m.combinedRowCardinalities([1, 3]))
		self.assertEquals([(0, 2), (1, 2)], m.combinedRowCardinalities([0, 1, 2, 3]))
		self.assertEquals([(0, 1)], m.combinedRowCardinalities([0]))
		self.assertEquals([(1, 1)], m.combinedRowCardinalities([1]))
		self.assertEquals([(0, 1), (1, 1)], m.combinedRowCardinalities([0, 1]))
		self.assertEquals([(0, 1)], m.combinedRowCardinalities([2]))
		self.assertEquals([(1, 1)], m.combinedRowCardinalities([3]))
		self.assertEquals([(0, 1), (1, 1)], m.combinedRowCardinalities([2, 3]))

	def testAllOnes(self):
		m = BitMatrix()
		m.addRow([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
		m.addRow([1, 3, 5, 8, 18])
		self.assertEquals([(0, 1)], m.combinedRowCardinalities([0]))
		self.assertEquals([(0, 3), (1, 1)], m.combinedRowCardinalities([0,1,2]))
		self.assertEquals([(0, 4), (1, 2)], m.combinedRowCardinalities([0,1,2,3]))
		self.assertEquals([(0, 5), (1, 2)], m.combinedRowCardinalities([0,1,2,3,4]))
		self.assertEquals([(0, 6), (1, 3)], m.combinedRowCardinalities([0,1,2,3,4,5]))
		self.assertEquals([(0, 7), (1, 3)], m.combinedRowCardinalities([0,1,2,3,4,5,6]))
		self.assertEquals([(0, 8), (1, 3)], m.combinedRowCardinalities([0,1,2,3,4,5,6,7]))
		self.assertEquals([(0, 9), (1, 4)], m.combinedRowCardinalities([0,1,2,3,4,5,6,7,8]))
		self.assertEquals([(0,10), (1, 4)], m.combinedRowCardinalities([0,1,2,3,4,5,6,7,8,9]))

	def testMaxResults(self):
		pass

	def testPerformanceOfExtremelyWorstCaseNamelyRandomBits(self):
		print '\nWe interrupt this test to annoy you and make things generally irritating for you.'
		docs = 10000
		terms = 100
		print 'Populating matrix of %s docs x %s terms, please wait...' % (docs, terms)
		m = BitMatrix(maxRows=terms)
		sumCardinalities = 0
		for i in range(terms):
			termDocs = [n for n in range(docs) if int(random()+0.3)]
			sumCardinalities += len(termDocs)
			m.addRow(termDocs)
		print 'Avarage cardinality of docsets in the matrix:', sumCardinalities/i

		docset = [i for i in range(docs) if int(random()+0.5)]
		print 'Executing combinedRowCardinalities(|docs|=%d), please wait...' % len(docset)
		start = time()
		for i in range(100):
			m.combinedRowCardinalities(docset, 0)
		t = time() - start
		print 'combinedRowCardinalities() took', t*10, 'ms.'

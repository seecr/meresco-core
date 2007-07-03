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
from core.index.xslice import XSlice
import unittest
from meresco.teddy import document
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

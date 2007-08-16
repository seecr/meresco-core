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
#
# $Id: configurationtest.py 78 2006-05-18 13:20:26Z svn $
#

from meresco.components.drilldown.cpp.bitarray import DenseBitArray, SparseBitArray
import unittest

class BitArrayTest(unittest.TestCase):

    def createDense(self, length, aList):
        result = DenseBitArray(length)
        for i in aList:
            result.set(i)
        return result
        
    def createSparse(self, length, aList):
        result = SparseBitArray(len(aList))
        for i in aList:
            result.set(i)
        return result
    
    def _checkCardinalities(self, list0, list1, createMethod0, createMethod1):
        cardinality0 = len(list0)
        cardinality1 = len(list1)
        combined = len(set(list0).intersection(set(list1)))
        bitarray0 = createMethod0(100000, list0)
        bitarray1 = createMethod1(100000, list1)
        
        self.assertEquals(cardinality0, bitarray0.cardinality())
        self.assertEquals(cardinality1, bitarray1.cardinality())
        self.assertEquals(combined, bitarray0.combinedCardinality(bitarray1))
        self.assertEquals(combined, bitarray1.combinedCardinality(bitarray0))
        
    
    def checkCardinalities(self, createMethod0, createMethod1):
        self._checkCardinalities(
            [0, 1, 2, 3, 50, 97, 99998, 99999],
            [0, 50, 99999],
            createMethod0, createMethod1)
        self._checkCardinalities(
            [0],
            [256],
            createMethod0, createMethod1)
        self._checkCardinalities(
            xrange(100000), 
            [1263, 4862, 8792, 9057, 9208, 9418, 9807, 12083, 12699, 13271, 14367, 14875, 15332, 15981, 16746, 17740, 17978, 18207, 19425, 19446, 19566, 19745, 20760, 20809, 22967, 23557, 25959, 26481, 26494, 26593, 27381, 27858, 28236, 29166, 30598, 30977, 31166, 32177, 33073, 33204, 33618, 36396, 38100, 38160, 39294, 41287, 41322, 43457, 43835, 44534, 45702, 45745, 46374, 47800, 48274, 49435, 49479, 49747, 52033, 52502, 52503, 53493, 53538, 53631, 53957, 54079, 56045, 57347, 58041, 60855, 66093, 66285, 66405, 66938, 67260, 68082, 68107, 68826, 71421, 73504, 75877, 76296, 77159, 79899, 81076, 82040, 82790, 83353, 86445, 88181, 90474, 91394, 92472, 93020, 93597, 95286, 97302, 98424, 99433, 99522],
            createMethod0, createMethod1)

    def testCreateDense(self):
        b = DenseBitArray(100)
        
    def testSetAndGetDense(self):
        b = DenseBitArray(100)
        b.set(0)
        b.set(50)
        b.set(99)
        self.assertTrue(b.get(0))
        self.assertFalse(b.get(1))
        self.assertTrue(b.get(50))
        self.assertTrue(b.get(99))
        
    def testCardinalityDense(self):
        b = DenseBitArray(100)
        self.assertEquals(0, b.cardinality())
        b.set(0)
        b.set(50)
        b.set(99)
        self.assertEquals(3, b.cardinality())
        b.set(0)
        #Note: this strange behavior is a 'feature', i.e. it is a result of extreme optimalisation.
        self.assertEquals(4, b.cardinality())
        
    def testCombinedCardinalityDense(self):
        self.checkCardinalities(self.createDense, self.createDense)
        
    #SPARSE:
    def testCreateSparse(self):
        b = SparseBitArray(100)
        
    def testCardinalitySparse(self):
        b = SparseBitArray(100)
        self.assertEquals(0, b.cardinality())
        b.set(0)
        b.set(50)
        b.set(99)
        self.assertEquals(3, b.cardinality())
        b.set(0)
        #Note: this strange behavior is a 'feature', i.e. it is a result of extreme optimalisation.
        self.assertEquals(4, b.cardinality())
        
    def testCombinedCardinalitySparse(self):
        self.checkCardinalities(self.createSparse, self.createSparse)

    #COMBINATION:
    def testCombinedCardinalityCombination(self):
        self.checkCardinalities(self.createSparse, self.createDense)
        self.checkCardinalities(self.createDense, self.createSparse)    

if __name__ == '__main__':
    unittest.main()

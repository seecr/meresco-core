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

from bitarray import DenseBitArray, SparseBitArray
from random import sample
from time import time
from sys import stdout

NR_OF_COMPARISONS = 100000

def powerrange(x, y):
    return map(lambda z: pow(10, z), range(x, y))

def write(s):
    stdout.write(s)
    stdout.flush()

class BitArray:
    def __init__(self, length, cardinality):
        self.length = length
        self.cardinality = cardinality
        self.set = sorted(sample(xrange(length), cardinality))
    
class ProfileBitArray:

    def __init__(self):
        self._testset = []
        for i in range(3, 6):
            length = pow(10, i)
            for cardinality1 in powerrange(0, i + 1):
                for cardinality2 in powerrange(0, i + 1):
                    self._testset.append((
                        (BitArray(length, cardinality1)),
                        (BitArray(length, cardinality2))))
        
    def test(self, bitarray1, bitarray2):
        start = time()
        for i in xrange(NR_OF_COMPARISONS):
            bitarray1.combinedCardinality(bitarray2)
        return time() - start

    def fill(self, bitarray, testSet):
        for i in testSet:
            bitarray.set(i)

    def createDense(self, test):
        result = DenseBitArray(test.length)
        self.fill(result, test.set)
        return result
        
    def createSparse(self, test):
        result = SparseBitArray(test.cardinality)
        self.fill(result, test.set)
        return result
    
    def main(self):
        resultLabels = ["dense/dense", "dense/sparse", "sparse/dense", "sparse/sparse"]
        write("Ready to go...numbers are for %s comparisons\n" % NR_OF_COMPARISONS)
        write("\t".join(["length", "cardinality1", "cardinality2"] + resultLabels + ["fastest"]) + "\n")
        for test in self._testset:
            d0 = self.createDense(test[0])
            d1 = self.createDense(test[1])
            s0 = self.createSparse(test[0])
            s1 = self.createSparse(test[1])
            dd = self.test(d0, d1)
            ds = self.test(d0, s1)
            sd = self.test(s0, d1)
            ss = self.test(s0, s1)
            results = [dd, ds, sd, ss]
            write(
                "\t".join(map(lambda d: "%8d" % d, [test[0].length, test[0].cardinality, test[1].cardinality])) + "\t" + 
                "\t".join(map(lambda f: "%2.8f" % f, results)) + "\t" +
                resultLabels[results.index(min(results))] + "\n")
            
if __name__ == '__main__':
    ProfileBitArray().main()

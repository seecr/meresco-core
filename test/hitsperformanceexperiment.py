## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
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
from os.path import isdir, join, abspath, dirname
from sys import path
from os import listdir, remove

depsDir = join(abspath(dirname(__file__)), '..', 'deps.d')
if isdir(depsDir):
    for d in listdir(depsDir):
        path.insert(0, join(depsDir, d))
path.insert(0, join(abspath(dirname(__file__)), '..'))

from time import time

t0 = time()
for i in range(10000000):
    pass

benchmarkIndex = time() - t0

def profile(method):
    t0 = time()
    method()
    totalTime = time() - t0
    return totalTime, totalTime / benchmarkIndex

#getAndIterateOverDocNumbers
from PyLucene import IndexReader, IndexSearcher, TermQuery, Term
from meresco.components.lucene.hits import Hits

reader = IndexReader.open('/home/pair/zandbak/index')
searcher = IndexSearcher(reader)
query = TermQuery(Term('meta.repository.collection', 'tilburg'))

def getAndIterateOverDocNumbers():
    hits = Hits(searcher, reader, query, None)
    hits.bitMatrixRow()

#twoMillionRow
from bitmatrix import Row
twoMillion = range(2000000)

def twoMillionRow():
    Row(twoMillion)

getAndIterateOverDocNumbersResult = profile(getAndIterateOverDocNumbers)
twoMillionRowResult = profile(twoMillionRow)

from commands import getstatusoutput

svnInfo = getstatusoutput('svn up log')[1]

logFilename = join(abspath(dirname(__file__)), 'log', 'hitsperformance.log')

f = open(logFilename, 'a')

f.write("*************************\n")
f.write(svnInfo + "\n")

f.write('getAndIterateOverDocNumbers ' + str(getAndIterateOverDocNumbersResult) + "\n")
f.write('twoMillionRow ' + str(twoMillionRowResult) + "\n")

f.close()



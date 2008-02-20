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



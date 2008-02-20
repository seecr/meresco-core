import os, sys
from os.path import isfile, join
from glob import glob
from time import time

os.system('find .. -name "*.pyc" | xargs rm -f')

for path in glob('../deps.d/*'):
    sys.path.insert(0, path)
sys.path.insert(0, '..')

INDEX_PATH='/home/pair/zandbak/index'

lockFile = join(INDEX_PATH, 'write.lock')
if isfile(lockFile):
    os.remove(lockFile)

from meresco.components.lucene import LuceneIndex
from meresco.components.drilldown import Drilldown

from PyLucene import TermQuery, Term

drilldownFields = [
    'drilldown.olc.yearNorm',
    'drilldown.olc.author',
    'drilldown.olc.source',
    'drilldown.olc.uncontrolledTerm'
]

t0 = time()
index = LuceneIndex(INDEX_PATH, 'cqlparser', 'reactor')
drilldown = Drilldown(drilldownFields)
drilldown.indexOptimized(index._reader)
print "Open index and drilldown in", time() - t0


query = TermQuery(Term('meta.repository.collection', 'tilburg'))

t0 = time()
hits = index.executeQuery(query)
#docIds = hits.docNumbers()
#for fieldname, results in drilldown.drilldown(docIds, zip(drilldownFields, [10] * len(drilldownFields))):

for fieldname, results in drilldown.drilldown(hits, zip(drilldownFields, [10] * len(drilldownFields))):
    t1 = time()
    print fieldname
    #print list(results)
    list(results)
    print "drilldown time", fieldname, time()-t1

print 'total drilldown time', time() - t0
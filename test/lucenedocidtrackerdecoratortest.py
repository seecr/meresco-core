from cq2utils import CQ2TestCase, CallTrace
from PyLucene import IndexWriter, IndexSearcher, StandardAnalyzer, Document, Field, Term, MatchAllDocsQuery, TermQuery, RAMDirectory, QueryFilter, IndexReader
from random import randint
from meresco.components.drilldown.lucenedocidtracker import LuceneDocIdTrackerDecorator
from glob import glob
from time import time
from cq2utils.profileit import profile

class LuceneDocIdTrackerDecoratorTest(CQ2TestCase):

    def testAssertIndexIsOptimized(self):
        writer = IndexWriter(self.tempdir, StandardAnalyzer(), True)
        reader = IndexReader.open(self.tempdir)
        try:
            LuceneDocIdTrackerDecorator(reader)
            self.fail('must raise exception')
        except Exception, e:
            self.assertEquals('index must be optimized', str(e))

    def testAssertMergeFactorAndMaxBufferedDocs(self):
        writer = IndexWriter(self.tempdir, StandardAnalyzer(), True)
        writer.setMaxBufferedDocs(9)
        writer.setMergeFactor(8)
        writer.addDocument(Document())
        writer.optimize()
        reader = IndexReader.open(self.tempdir)
        class Index(object):
            isOptimized = reader.isOptimized
            getMergeFactor = writer.getMergeFactor
            getMaxBufferedDocs = writer.getMaxBufferedDocs
        try:
            LuceneDocIdTrackerDecorator(Index())
            self.fail('must raise exception')
        except Exception, e:
            self.assertEquals('mergeFactor != maxBufferedDocs', str(e))

    def testDecorateLucene(self):
        doc = Document()
        doc.add(Field('__id__', "one", Field.Store.YES, Field.Index.UN_TOKENIZED))
        lucene = CallTrace('Lucene', returnValues={'getMergeFactor': 15, 'getMaxBufferedDocs': 15, 'isOptimized': True})
        wrappedLucene = LuceneDocIdTrackerDecorator(lucene)
        result = wrappedLucene.addDocument(doc)
        self.assertEquals(0, result)
        result = wrappedLucene.addDocument(doc)
        self.assertEquals(1, result)
        self.assertEquals('isOptimized()', str(lucene.calledMethods[0]))
        self.assertEquals('getMergeFactor()', str(lucene.calledMethods[1]))
        self.assertEquals('getMaxBufferedDocs()', str(lucene.calledMethods[2]))
        self.assertEquals('addDocument(<class Document>)', str(lucene.calledMethods[3]))

    def testDecorateLuceneDelete(self):
        lucene = CallTrace('Lucene', returnValues={'getMergeFactor': 2, 'getMaxBufferedDocs': 2, 'delete': 1, 'isOptimized': True})
        wrappedLucene = LuceneDocIdTrackerDecorator(lucene)
        wrappedLucene.addDocument('doc0')
        wrappedLucene.addDocument('doc1')
        wrappedLucene.addDocument('doc2')
        result = wrappedLucene.delete('doc1') # nr 1 according to lucene
        self.assertEquals(1, result)
        wrappedLucene.addDocument('doc3')     # triggers merge
        result = wrappedLucene.delete('doc2') # nr 1 according to lucene
        self.assertEquals(2, result)
        self.assertEquals("delete('doc1')", str(lucene.calledMethods[6]))
        self.assertEquals("delete('doc2')", str(lucene.calledMethods[8]))

    def testQuery(self):
        innerHits = CallTrace('hits', returnValues={'bitMatrixRow': [0]})
        lucene = CallTrace('Lucene', returnValues={'getMergeFactor': 2, 'getMaxBufferedDocs': 2, 'delete': 0, 'executeQuery': innerHits, 'isOptimized': True})
        wrappedLucene = LuceneDocIdTrackerDecorator(lucene)
        wrappedLucene.addDocument('doc0')
        hits = wrappedLucene.executeQuery(self, 'query', sortBy=None, sortDescending=None)
        docset = hits.bitMatrixRow()
        self.assertEquals([0], docset)
        self.assertEquals('bitMatrixRow([0])', str(innerHits.calledMethods[0]))

    def testReadLuceneDocSetsAndMapThem(self):
        writer = IndexWriter(self.tempdir, StandardAnalyzer(), True)
        for i in range(3):
            doc = Document()
            doc.add(Field('field', 'term%s' % i, Field.Store.YES, Field.Index.UN_TOKENIZED))
            writer.addDocument(Document())
        class Index(object):
            isOptimized = lambda self: True
            getMergeFactor = writer.getMergeFactor
            getMaxBufferedDocs = writer.getMaxBufferedDocs
        wrappedLucene = LuceneDocIdTrackerDecorator(Index())
        docsets = wrappedLucene.getDocSets(['field'])
        self.assertEquals([('field', ['?'])], list(docsets))







from cq2utils import CQ2TestCase, CallTrace
from PyLucene import IndexWriter, IndexSearcher, StandardAnalyzer, Document, Field, Term, MatchAllDocsQuery, TermQuery, RAMDirectory, QueryFilter, IndexReader
from random import randint
from meresco.components.lucene.lucenedocidtracker import LuceneDocIdTrackerDecorator
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
        lucene = CallTrace('Lucene', returnValues={'getMergeFactor': 15, 'getMaxBufferedDocs': 15, 'isOptimized': True, 'docCount': 0})
        wrappedLucene = LuceneDocIdTrackerDecorator(lucene)
        result = wrappedLucene.addDocument(doc)
        self.assertEquals(0, result)
        result = wrappedLucene.addDocument(doc)
        self.assertEquals(1, result)
        self.assertEquals('isOptimized()', str(lucene.calledMethods[0]))
        self.assertEquals('getMergeFactor()', str(lucene.calledMethods[1]))
        self.assertEquals('getMaxBufferedDocs()', str(lucene.calledMethods[2]))
        self.assertEquals('addDocument(<class Document>)', str(lucene.calledMethods[4]))

    def testDecorateLuceneDelete(self):
        lucene = CallTrace('Lucene', returnValues={'getMergeFactor': 2, 'getMaxBufferedDocs': 2, 'delete': 1, 'isOptimized': True, 'docCount': 0})
        wrappedLucene = LuceneDocIdTrackerDecorator(lucene)
        wrappedLucene.addDocument('doc0')
        wrappedLucene.addDocument('doc1')
        wrappedLucene.addDocument('doc2')
        result = wrappedLucene.delete('doc1') # nr 1 according to lucene
        self.assertEquals(1, result)
        wrappedLucene.addDocument('doc3')     # triggers merge
        result = wrappedLucene.delete('doc2') # nr 1 according to lucene
        self.assertEquals(2, result)
        self.assertEquals("delete('doc1')", str(lucene.calledMethods[7]))
        self.assertEquals("delete('doc2')", str(lucene.calledMethods[9]))

    def testQuery(self):
        innerHits = CallTrace('hits', returnValues={'bitMatrixRow': [0]})
        lucene = CallTrace('Lucene', returnValues={'getMergeFactor': 2, 'getMaxBufferedDocs': 2, 'delete': 0, 'executeQuery': innerHits, 'isOptimized': True, 'docCount': 0})
        wrappedLucene = LuceneDocIdTrackerDecorator(lucene)
        wrappedLucene.addDocument('doc0')
        hits = wrappedLucene.executeQuery(self, 'query', sortBy=None, sortDescending=None)
        docset = hits.bitMatrixRow()
        self.assertEquals([0], docset)
        self.assertEquals('bitMatrixRow([0])', str(innerHits.calledMethods[0]))

    def XXXXXXXXXXXXXXXXXXtestReadLuceneDocSetsAndMapThem(self):
        writer = IndexWriter(self.tempdir, StandardAnalyzer(), True)
        writer.setMergeFactor(2)
        writer.setMaxBufferedDocs(2)
        for i in range(3):
            doc = Document()
            doc.add(Field('field', 'term%s' % i, Field.Store.YES, Field.Index.UN_TOKENIZED))
            writer.addDocument(doc)
        writer.deleteDocuments(Term('field', 'term1'))
        doc = Document()
        doc.add(Field('field', 'term3', Field.Store.YES, Field.Index.UN_TOKENIZED))
        writer.addDocument(doc)
        writer.flush()
        reader = IndexReader.open(self.tempdir)
        class Index(object):
            isOptimized = lambda self: False
            getMergeFactor = writer.getMergeFactor
            getMaxBufferedDocs = writer.getMaxBufferedDocs
            getReader = lambda self: reader
        wrappedLucene = LuceneDocIdTrackerDecorator(Index())
        docsets = wrappedLucene.getDocSets(['field'])
        self.assertEquals([('field', [(u'term0', [0]), (u'term2', [2]), (u'term3', [3])])], [(x, list(y)) for (x, y) in docsets])


    def testReadLuceneDocSetsFromOptimizedIndex(self):
        writer = IndexWriter(self.tempdir, StandardAnalyzer(), True)
        for i in range(3):
            doc = Document()
            doc.add(Field('field', 'term%s' % i, Field.Store.YES, Field.Index.UN_TOKENIZED))
            writer.addDocument(doc)
        writer.optimize()
        reader = IndexReader.open(self.tempdir)
        class Index(object):
            isOptimized = reader.isOptimized
            getMergeFactor = writer.getMergeFactor
            getMaxBufferedDocs = writer.getMaxBufferedDocs
            getReader = lambda self: reader
            docCount = reader.numDocs
            delete = lambda self, appId: 1
            addDocument = lambda self, doc: None
        wrappedLucene = LuceneDocIdTrackerDecorator(Index())
        docsets = wrappedLucene.getDocSets(['field'])
        self.assertEquals([('field', [(u'term0', [0]), (u'term1', [1]), (u'term2', [2])])], [(x, list(y)) for (x, y) in docsets])

        result = wrappedLucene.addDocument(Document())
        self.assertEquals(3, result)






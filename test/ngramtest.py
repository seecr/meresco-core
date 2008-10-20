from cq2utils import CQ2TestCase, CallTrace
from time import time
from sys import stdout
from PyLucene import IndexReader, IndexWriter, IndexSearcher, BooleanQuery, BooleanClause, TermQuery, Term, Field, StandardAnalyzer, Document
from Levenshtein import distance, ratio

def ngrams(word, N=2):
    for n in range(2, N+1):
        for i in range(len(word)-n+1):
            yield word[i:i+n]

def addWord(index, word):
    d = Document()
    d.add(Field('term', word, Field.Store.YES, Field.Index.TOKENIZED))
    d.add(Field('ngrams', ' '.join(ngrams(word)), Field.Store.NO, Field.Index.TOKENIZED))
    index.addDocument(d)

def ngramQuery(word, N=2):
    query = BooleanQuery()
    for ngram in ngrams(word, N):
        query.add(BooleanClause(TermQuery(Term('ngrams', ngram)), BooleanClause.Occur.SHOULD))
    return query




from meresco.framework import Transparant

class NGramFieldlet(Transparant):
    def __init__(self, ngrams, termField, ngramField):
        Transparant.__init__(self)
        self._ngrams = ngrams
        self._termField = termField
        self._ngramField = ngramField

    def addField(self, field, value):
        for word in value.split():
            self.do.addField(self._termField, word)
            for ngram in self._ngram(word):
                self.do.addField(self._ngramField, ngram)

    def _ngram(self, word):
        for n in range(2, self._ngrams+1):
            for i in range(len(word)-n+1):
                yield word[i:i+n]


class NGramTest(CQ2TestCase):
    def testDNA(self):
        dna = \
            (NGramFieldlet(2, 'word', 'ngrams'),
                (TransactionFactory(lambda tx: Fields2LuceneDocumentTx(tx, untokenized=['word', 'ngrams'])),
                    (LuceneIndex(self.tempdir, mockreactor),)
                )
            )
        x = be(dna)
        self.assertFalse('hier verder')

    def testCreateIndex(self):
        index = IndexWriter(self.tempdir, StandardAnalyzer(), True)
        addWord(index, 'appelboom')
        index.flush()
        searcher = IndexSearcher(self.tempdir)
        hits = searcher.search(TermQuery(Term('ngrams', 'ap')))
        self.assertEquals('appelboom', hits[0].get('term'))

    def testNgram(self):
        self.assertEquals(set(['bo', 'oo', 'om', 'boo', 'oom', 'boom']), set(ngrams('boom', N=4)))
        self.assertEquals(set(['bo', 'oo', 'om']), set(ngrams('boom', N=2)))

    def testNGramFieldLet(self):
        observert = CallTrace('Observert')
        ngramFieldlet = NGramFieldlet(2, 'word', 'ngrams')
        ngramFieldlet.addObserver(observert)

        ngramFieldlet.addField('field0', 'term0')
        self.assertEquals(5, len(observert.calledMethods))
        self.assertEquals("addField('word', 'term0')", str(observert.calledMethods[0]))
        self.assertEquals("addField('ngrams', 'te')", str(observert.calledMethods[1]))
        self.assertEquals("addField('ngrams', 'er')", str(observert.calledMethods[2]))
        self.assertEquals("addField('ngrams', 'rm')", str(observert.calledMethods[3]))
        self.assertEquals("addField('ngrams', 'm0')", str(observert.calledMethods[4]))


    def testIntegrationWords(self):
        #index = IndexWriter('index', StandardAnalyzer(), True)
        #f = open('/usr/share/dict/words')
        #for word in f:
            ##print word
            #addWord(index, word.strip().decode('iso 8859-1'))
        #index.flush()
        #index.close()
        searcher = IndexSearcher('index')
        # Alabama
        for word in ['Alabama', 'alhambra', 'albuqurqi', 'matematics', 'restauration', 'abridgement', 'entousiast', 'puch', 'grnt', 'carot', 'from', 'sema', 'bord', 'enrgie', 'energie', 'enery', 'energy' ]:
            print "'%s', did you mean:" % word
            for N in range(2,4):
                hits = iter(searcher.search(ngramQuery(word, N=N)))
                suggestions = []
                for n in range(125):
                    hit = hits.next()
                    score = hit.getScore()
                    term = hit.get('term')
                    suggestions.append((term, score, distance(unicode(term), unicode(word)), ratio(unicode(term), unicode(word))))
                levenSuggs = sorted(suggestions, key=lambda x: x[2])[:5]
                ratioSuggs = sorted(suggestions, key=lambda x: x[3], reverse=True)[:5]
                print '    Score:', ', '.join('%s (%.1f)' % (sugg[0], sugg[1]) for sugg in suggestions[:5])
                print '    Leven (n=%d):'%N, ', '.join('%s (%.1f)' % (sugg[0], sugg[2]) for sugg in levenSuggs if sugg[2] < 5)
                print '    Ratio (n=%d):'%N, ', '.join('%s (%.1f)' % (sugg[0], sugg[3]) for sugg in ratioSuggs if sugg[3] > 0.65)







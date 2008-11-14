#-*- coding: utf-8
from cq2utils import CQ2TestCase, CallTrace

from meresco.framework import Observable, TransactionScope, ResourceManager, be
from meresco.components.ngram import NGramFieldlet, NGramQuery, ngrams, LevenshteinSuggester, RatioSuggester
from meresco.components.lucene import LuceneIndex, Fields2LuceneDocumentTx
from meresco.components import Xml2Fields

from Levenshtein import distance, ratio
from lxml.etree import parse
from StringIO import StringIO
from PyLucene import BooleanQuery, BooleanClause, IndexReader, IndexWriter, IndexSearcher, TermQuery, Term, Field, StandardAnalyzer, Document


PUCH_WORDS = ['capuche', 'capuches', 'Capuchin', 'capuchins', 'Mapuche', 'Pampuch', 'puchera', 'pucherite', 'capuched', 'capuchin', 'puchero', 'PUC', 'Kampuchea', 'kampuchea', 'Puchanahua', 'sepuchral', 'puca', 'puce', 'puces', 'Puck', 'puck', 'pucka', 'pucks', 'Pupuluca', 'Puccini', 'puccini', 'puccoon', 'puceron', 'Pucida', 'pucker', 'puckish', 'puckle', 'SPUCDL', 'Chuch', 'Punch', 'punch', 'cappuccino', 'capucine', 'catapuce', 'catepuce', 'depucel', 'leucopus', 'mucopus', 'praepuce', 'prepuce', 'prepuces', 'Puccinia', 'puccinoid', 'puccoons', 'pucelage', 'pucellas', 'pucelle', 'puckball', 'puckered', 'puckerel', 'puckerer', 'puckering', 'puckers', 'puckery', 'Puckett', 'puckfist', 'puckfoist', 'puckishly', 'pucklike', 'puckling', 'puckrel', 'pucksey', 'puckster', 'sapucaia', 'unpucker', 'Vespucci', 'vespucci', 'Chucho', 'aneuch', 'aucht', 'bauch', 'bouch', 'Bruch', 'Buch', 'Buchan', 'buch', 'cauch', 'Chuck', 'chuck', 'couch', 'Cuchan', 'duchan', 'duchy', 'Eucha', 'Fauch', 'fuchi', 'Fuchs', 'heuch', 'hucho', 'Jauch', 'kauch', 'leuch', 'louch', 'Lucho', 'Manouch', 'mouch', 'much', 'nauch', 'nonsuch', 'nouche', 'nucha', 'ouch', 'pouch', 'Rauch', 'ruche', 'sauch', 'snouch', 'such', 'teuch', 'touch', 'touch-', 'touche', 'touchy', 'tuchis', 'tuchit', 'Uchean', 'Uchee', 'Uchish', 'vouch', 'wauch']

def createNGramHelix(observert):
    return be(
        (Observable(),
            (TransactionScope('ngram'),
                (NGramFieldlet(2, 'ngrams'),
                    (observert,)
                )
            )
        )
    )



class NGramTest(CQ2TestCase):
    def testDNA(self):
        def ngramQuery(word, N=2):
            query = BooleanQuery()
            for ngram in ngrams(word, N):
                query.add(BooleanClause(TermQuery(Term('ngrams', ngram)), BooleanClause.Occur.SHOULD))
            return query

        reactor = CallTrace('Reactor')
        index = LuceneIndex(self.tempdir, reactor)
        dna = \
            (Observable(),
                (TransactionScope('ngram'),
                    (Xml2Fields(),
                        (NGramFieldlet(2, 'ngrams'),
                            (ResourceManager('ngram', lambda resourceManager: Fields2LuceneDocumentTx(resourceManager, untokenized=[])),
                                (index,)
                            )
                        )
                    )
                ),
                (NGramQuery(2, 'ngrams'),
                    (index,)
                )
            )
        x = be(dna)
        xmlNode = parse(StringIO(u'<node><subnode>ideeën</subnode></node>'))
        x.do.addXml(xmlNode)
        index.start()
        hits = index.executeQuery(ngramQuery(u'ideeën'))
        self.assertEquals(1, index.docCount())
        self.assertEquals('ideeën', hits[0])

    def testCreateIndex(self):
        def addWord(index, word):
            d = Document()
            d.add(Field('term', word, Field.Store.YES, Field.Index.TOKENIZED))
            d.add(Field('ngrams', ' '.join(ngrams(word)), Field.Store.NO, Field.Index.TOKENIZED))
            index.addDocument(d)
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
        ngramFieldlet = createNGramHelix(observert)
        ngramFieldlet.do.addField('field0', 'term0')
        self.assertEquals(2, len(observert.calledMethods))
        self.assertEquals("begin()", str(observert.calledMethods[0]))
        self.assertEquals('addField', observert.calledMethods[1].name)
        self.assertEquals(('ngrams', 'te er rm m0'), observert.calledMethods[1].args)

    def testWordisIDinTransactionScope(self):
        txlocals = {}
        class Observert(Observable):
            def addField(self, *args):
                txlocals.update(self.tx.locals)
        x = createNGramHelix(Observert())
        x.do.addField('field0', 'term0')
        self.assertEquals({'id': u'term0'}, txlocals)

    def testNgramQuery(self):
        ngramindex = CallTrace('ngramindex', returnValues = {'executeQuery': (x for x in ['term0', 'term1'])})
        ngramQuery = NGramQuery(2, 'ngrams')
        ngramQuery.addObserver(ngramindex)
        hits = ngramQuery.executeQuery('term0')
        self.assertEquals(['term0', 'term1'], list(hits))
        self.assertEquals('ngrams:te ngrams:er ngrams:rm ngrams:m0', str(ngramindex.calledMethods[0].arguments[0]))
        ngramindex.returnValues['executeQuery'] = ['term2', 'term9']
        hits = ngramQuery.executeQuery('term0')
        self.assertEquals(['term2', 'term9'], list(hits))

    def testNgramQueryFieldname(self):
        ngramindex = CallTrace('ngramindex', returnValues = {'executeQuery': (x for x in ['term0', 'term1'])})
        ngramQuery = NGramQuery(2, 'some_fieldname')
        ngramQuery.addObserver(ngramindex)
        hits = ngramQuery.executeQuery('term0')
        self.assertEquals(['term0', 'term1'], list(hits))
        self.assertEquals('some_fieldname:te some_fieldname:er some_fieldname:rm some_fieldname:m0', str(ngramindex.calledMethods[0].arguments[0]))
        ngramindex.returnValues['executeQuery'] = ['term2', 'term9']

    def assertSuggestions(self, expected, term, suggester):
        ngramindex = CallTrace('ngramindex', returnValues = {'executeQuery': (x for x in PUCH_WORDS)})
        ngramQuery = NGramQuery(2, 'ngrams')
        ngramQuery.addObserver(ngramindex)
        suggester.addObserver(ngramQuery)
        results = suggester.suggestionsFor(term)
        self.assertEquals(expected, list(results))

    def testLevenshtein(self):
        self.assertSuggestions(['puca', 'puce', 'puck', 'punch', 'puces'], 'puch', LevenshteinSuggester(50, 3, 5))

    def testRatio(self):
        self.assertSuggestions(['punch', 'puca', 'puce', 'puck', 'capuche'], 'puch', RatioSuggester(50, 0.6, 5))

    def testThresholdRatio(self):
        self.assertSuggestions([], 'puch', RatioSuggester(50, 0.9, 5))
        self.assertSuggestions(['punch'], 'puch', RatioSuggester(50, 0.8, 5))
        self.assertSuggestions(['punch', 'puca', 'puce', 'puck', 'capuche'], 'puch', RatioSuggester(50, 0.7, 5))
        self.assertSuggestions(['punch', 'puca', 'puce', 'puck', 'capuche'], 'puch', RatioSuggester(50, 0.6, 5))
        self.assertSuggestions(['punch', 'puca', 'puce', 'puck', 'capuche'], 'puch', RatioSuggester(50, 0.5, 5))


    def testThresholdLevenshtein(self):
        self.assertSuggestions([], 'puch', LevenshteinSuggester(50, 0, 5))
        self.assertSuggestions(['puca', 'puce', 'puck', 'punch'], 'puch', LevenshteinSuggester(50, 1, 5))
        self.assertSuggestions(['puca', 'puce', 'puck', 'punch', 'puces'], 'puch', LevenshteinSuggester(50, 2, 5))
        self.assertSuggestions(['puca', 'puce', 'puck', 'punch', 'puces'], 'puch', LevenshteinSuggester(50, 3, 5))
        self.assertSuggestions(['puca', 'puce', 'puck', 'punch', 'puces', 'Puck', 'pucka'], 'puch', LevenshteinSuggester(50, 4, 7))

    def testDoNotSuggestSameWord(self):
        self.assertSuggestions(['Punch', 'puca', 'puce', 'puck'], 'punch', LevenshteinSuggester(50, 5, 4))
        self.assertSuggestions(['Punch', 'capuche', 'Mapuche', 'Pampuch'], 'punch', RatioSuggester(50, 0.5, 4))


    def XXXXXXXXtestIntegrationWords(self):
        def addWord(index, word):
            d = Document()
            d.add(Field('term', word, Field.Store.YES, Field.Index.TOKENIZED))
            d.add(Field('ngrams', ' '.join(ngrams(word)), Field.Store.NO, Field.Index.TOKENIZED))
            index.addDocument(d)
        index = IndexWriter('index', StandardAnalyzer(), True)
        f = open('/usr/share/dict/words')
        for word in f:
            #print word
            addWord(index, word.strip().decode('iso 8859-1'))
        index.flush()
        index.close()

        searcher = IndexSearcher('index')

        def ngramQuery(word, N=2):
            query = BooleanQuery()
            for ngram in ngrams(word, N):
                query.add(BooleanClause(TermQuery(Term('ngrams', ngram)), BooleanClause.Occur.SHOULD))
            return query

        for word in ['Alabama', 'alhambra', 'albuqurqi', 'matematics', 'restauration', 'abridgement', 'entousiast', 'puch', 'grnt', 'carot', 'from', 'sema', 'bord', 'enrgie', 'energie', 'enery', 'energy' ]:
            print "'%s', did you mean:" % word
            for N in range(2,4):
                hits = iter(searcher.search(ngramQuery(word, N=N)))
                suggestions = []
                for n in range(50): #seems roughly good in this test for 'grnt'
                    hit = hits.next()
                    score = hit.getScore()
                    term = hit.get('term')
                    suggestions.append((term, score, distance(unicode(term), unicode(word)), ratio(unicode(term), unicode(word))))
                if word == 'puch':
                    print [x[0] for x in suggestions]
                levenSuggs = sorted(suggestions, key=lambda x: x[2])[:5]
                ratioSuggs = sorted(suggestions, key=lambda x: x[3], reverse=True)[:5]
                print '    Score:', ', '.join('%s (%.1f)' % (sugg[0], sugg[1]) for sugg in suggestions[:5])
                print '    Leven (n=%d):'%N, ', '.join('%s (%.1f)' % (sugg[0], sugg[2]) for sugg in levenSuggs if sugg[2] < 5)
                print '    Ratio (n=%d):'%N, ', '.join('%s (%.1f)' % (sugg[0], sugg[3]) for sugg in ratioSuggs if sugg[3] > 0.65)






    def XXXXtestIntegrationLiveWords(self):
        def addWord(index, word):
            d = Document()
            d.add(Field('term', word, Field.Store.YES, Field.Index.TOKENIZED))
            d.add(Field('ngrams', ' '.join(ngrams(word)), Field.Store.NO, Field.Index.TOKENIZED))
            index.addDocument(d)
        index = IndexWriter('index2', StandardAnalyzer(), True)
        f = open('/home/meresco/words.txt')
        for word in f:
            #print word
            addWord(index, word.strip().decode('iso 8859-1'))
        index.flush()
        index.close()

        searcher = IndexSearcher('index2')

        def ngramQuery(word, N=2):
            query = BooleanQuery()
            for ngram in ngrams(word, N):
                query.add(BooleanClause(TermQuery(Term('ngrams', ngram)), BooleanClause.Occur.SHOULD))
            return query

        for word in ['Nederland', 'Rafael', 'config', 'susceptibility' ]:
            print "'%s', did you mean:" % word
            for N in range(2,4):
                hits = iter(searcher.search(ngramQuery(word, N=N)))
                suggestions = []
                for n in range(50): #seems roughly good in this test for 'grnt'
                    hit = hits.next()
                    score = hit.getScore()
                    term = hit.get('term')
                    suggestions.append((term, score, distance(unicode(term), unicode(word)), ratio(unicode(term), unicode(word))))
                if word == 'puch':
                    print [x[0] for x in suggestions]
                levenSuggs = sorted(suggestions, key=lambda x: x[2])[:5]
                ratioSuggs = sorted(suggestions, key=lambda x: x[3], reverse=True)[:5]
                print '    Score:', ', '.join('%s (%.1f)' % (sugg[0], sugg[1]) for sugg in suggestions[:5])
                print '    Leven (n=%d):'%N, ', '.join('%s (%.1f)' % (sugg[0], sugg[2]) for sugg in levenSuggs if sugg[2] < 5)
                print '    Ratio (n=%d):'%N, ', '.join('%s (%.1f)' % (sugg[0], sugg[3]) for sugg in ratioSuggs if sugg[3] > 0.65)

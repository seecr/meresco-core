from meresco.framework import Transparant,  Observable
from PyLucene import BooleanQuery, BooleanClause, TermQuery, Term
from Levenshtein import distance, ratio

def ngrams(word, N=2):
    for n in range(2, N+1):
        for i in range(len(word)-n+1):
            yield word[i:i+n]

class NGramQuery(Observable):
    def __init__(self, n, fieldName):
        Observable.__init__(self)
        self._fieldName = fieldName

    def executeQuery(self, query):
        hits = self.any.executeQuery(self.ngramQuery(query))
        return hits

    def ngramQuery(self, word, N=2):
        query = BooleanQuery()
        for ngram in ngrams(word, N):
            query.add(BooleanClause(TermQuery(Term(self._fieldName, ngram)), BooleanClause.Occur.SHOULD))
        return query

class _Suggestion(Observable):
    def __init__(self, items, threshold, maximumCount):
        Observable.__init__(self)
        self._items = items
        self._maximumCount = maximumCount
        self._threshold = threshold

    def suggestionsFor(self, word):
        hits = self.any.executeQuery(word)
        for i, hit in enumerate(hits):
            if i > self._items:
                break
            yield hit

class LevenshteinSuggester(_Suggestion):
    def suggestionsFor(self, word):
        word = unicode(word)
        result = _Suggestion.suggestionsFor(self, word)
        result = sorted(result, key=lambda term: distance(unicode(term), word))
        result = result[:self._maximumCount]
        result = [term for term in result if distance(unicode(term), word) <= self._threshold]
        return result

class RatioSuggester(_Suggestion):
    def suggestionsFor(self, word):
        word = unicode(word)
        result = _Suggestion.suggestionsFor(self, word)
        result = sorted(result, key=lambda term: ratio(unicode(term), word), reverse=True)
        result = result[:self._maximumCount]
        result = [term for term in result if ratio(unicode(term), word) > self._threshold]
        return result

class NGramFieldlet(Transparant):
    def __init__(self, n, fieldName):
        Transparant.__init__(self)
        self._n = n
        self._fieldName = fieldName

    def addField(self, name, value):
        for word in unicode(value).split():
            self.tx.locals['id'] = word
            ngrams = ' '.join(self._ngram(word))
            self.do.addField(self._fieldName, ngrams)
            #for ngram in self._ngram(word):
                #self.do.addField(self._fieldName, ngram)

    def _ngram(self, word):
        for n in range(2, self._n+1):
            for i in range(len(word)-n+1):
                yield word[i:i+n]

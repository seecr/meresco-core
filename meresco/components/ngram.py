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
    def suggestionsFor(self, word, count, algorithm, reverse):
        hits = self.any.executeQuery(word)
        return (term for term, distance in sorted(
            ((term, algorithm(term, word)) for term in hits),
            key=lambda (term, distance): distance, reverse=reverse)[:count])

class LevenshteinSuggester(_Suggestion):
    def suggestionsFor(self, word, count):
        return _Suggestion.suggestionsFor(self,
            word,
            count,
            lambda term, word: distance(unicode(term), unicode(word)),
            False)

class RatioSuggester(_Suggestion):
    def suggestionsFor(self, word, count):
        return _Suggestion.suggestionsFor(self,
            word,
            count,
            lambda term, word: ratio(unicode(term), unicode(word)),
            True)


class NGramFieldlet(Transparant):
    def __init__(self, n, fieldName):
        Transparant.__init__(self)
        self._n = n
        self._fieldName = fieldName

    def addField(self, name, value):
        for word in unicode(value).split():
            self.do.addField('__id__', word)
            for ngram in self._ngram(word):
                self.do.addField(self._fieldName, ngram)

    def _ngram(self, word):
        for n in range(2, self._n+1):
            for i in range(len(word)-n+1):
                yield word[i:i+n]

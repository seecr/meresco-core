from meresco.framework import Observable
from meresco.components.statistics import Logger
from meresco.components.lucene.cqlparsetreetolucenequery import Composer
from meresco.components.lucene.clausecollector import ClauseCollector

class CQL2LuceneQuery(Observable, Logger):

    def __init__(self, unqualifiedFields):
        Observable.__init__(self)
        self._cqlComposer = Composer(unqualifiedFields)

    def executeCQL(self, cqlAbstractSyntaxTree, sortBy=None, sortDescending=None):
        ClauseCollector(cqlAbstractSyntaxTree, self.log).visit()
        return self.any.executeQuery(self._cqlComposer.compose(cqlAbstractSyntaxTree), sortBy, sortDescending)
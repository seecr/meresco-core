## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) SURF Foundation. http://www.surf.nl
#    Copyright (C) Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) SURFnet. http://www.surfnet.nl
#    Copyright (C) Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
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

import os
from warnings import warn
import PyLucene
import xml.sax.saxutils

from cqlparser.lucenecomposer import compose as cqlAbstractSyntaxTreeToLucene

from meresco.components.lucene.hits import Hits
from meresco.components.lucene.document import IDFIELD, CONTENTFIELD


DEFAULT_OFFSET = 0
DEFAULT_COUNT = 10

class LuceneException(Exception):
    pass

class LuceneQuery:
    def __init__(self, aLuceneIndex, aQueryString, anOffset = DEFAULT_OFFSET,
                aCount = DEFAULT_COUNT, sortBy = None, sortDescending = None):
        """Very very deprecated"""
        self._index = aLuceneIndex
        self._offset = anOffset
        self._count = aCount
        self._queryString = aQueryString
        self._hitCount = 0
        self._batchSize = 0
        self._sortBy = sortBy
        self._sortDescending = sortDescending
        analyzer = PyLucene.StandardAnalyzer()
        queryParser = PyLucene.QueryParser(CONTENTFIELD, analyzer)
        queryParser.setDefaultOperator(PyLucene.QueryParser.Operator.AND)
        self._query = queryParser.parse(self._queryString)

    def perform(self):
        hits = self._index.search(self._getQuery(), self._getSort())
        self._hitCount = hits.length()
        batch = range(self._offset, min(self._offset + self._count, self._hitCount))
        for h in batch:
            yield hits.doc(h).get(IDFIELD)
        self._batchSize = len(batch)

    def getBatchSize(self):
        return self._batchSize

    def getOffset(self):
        return self._offset

    def getCount(self):
        return self._count

    def getHitCount(self):
        return self._hitCount

    def _getSort(self):
        sortDir = bool(self._sortDescending)
        return self._sortBy and \
            PyLucene.Sort(self._sortBy, sortDir) or None

    def _getQuery(self):
        return self._query

class LuceneIndex:

    def __init__(self, aDirectoryName):
        self.__searcher = None
        self.__reader = None
        self.__writer = None
        self._directoryName = aDirectoryName
        if not os.path.isdir(self._directoryName):
            os.makedirs(self._directoryName)
        if not PyLucene.IndexReader.indexExists(self._directoryName):
            self._getWriter(createIndex = True)
        self._indexChanged = False

    def query(self, aQuery):
        return self._getSearcher().search(aQuery)

    def queryWith(self, aLuceneQuery):
        for hit in aLuceneQuery.search():
            yield hit

    def deleteID(self, anId):
        self._getReader().deleteDocuments(PyLucene.Term(IDFIELD, anId))

    def countField(self, fieldName):
        """Deprecated (only used by legacay.plugins.fieldcountplugin) when killing kill TermIter too"""
        countDict = {}
        termEnum = self._getReader().terms(PyLucene.Term(fieldName, ''))
        termIter = TermIter(termEnum, fieldName)
        for term in termIter:
            countDict[term.text()] = self._getReader().docFreq(term)
        return countDict.items()

    def executeQuery(self, pyLuceneQuery, sortBy=None, sortDescending=None):
        return Hits(self._getSearcher(), pyLuceneQuery, self._getPyLuceneSort(sortBy, sortDescending))

    def executeCQL(self, cqlAbstractSyntaxTree, sortBy=None, sortDescending=None):
        return Hits(self._getSearcher(),
            self._parseLuceneQueryString(cqlAbstractSyntaxTreeToLucene(cqlAbstractSyntaxTree)),
            self._getPyLuceneSort(sortBy, sortDescending))

    def addToIndex(self, aDocument):
        aDocument.validate()
        aDocument.addToIndexWith(self._getWriter())

    def optimize(self):
        self._getWriter().optimize()

    def _getPyLuceneSort(self, sortBy, sortDescending):
        return sortBy and PyLucene.Sort(sortBy, bool(sortDescending)) or None

    def _parseLuceneQueryString(self, luceneQueryString):
        analyzer = PyLucene.StandardAnalyzer()
        queryParser = PyLucene.QueryParser(CONTENTFIELD, analyzer)
        queryParser.setDefaultOperator(PyLucene.QueryParser.Operator.AND)
        return queryParser.parse(luceneQueryString)

    def _getWriter(self, createIndex = False):
        if self.__reader:
            self.__reader.close()
            self.__reader = None
        if self.__searcher:
            self.__searcher.close()
            self.__searcher = None
        if not self.__writer:
            self.__writer = PyLucene.IndexWriter(self._directoryName, PyLucene.StandardAnalyzer(), createIndex)
        return self.__writer

    def _getSearcher(self):
        if self.__reader:
            self.__reader.close()
            self.__reader = None
        if self.__writer:
            self.__writer.close()
            self.__writer = None
        if not self.__searcher:
            self._searcher = PyLucene.IndexSearcher(self._directoryName)
        return self._searcher

    def _getReader(self):
        if self.__writer:
            self.__writer.close()
            self.__writer = None
        if self.__searcher:
            self.__searcher.close()
            self.__searcher = None
        if not self.__reader:
            self.__reader = PyLucene.IndexReader.open(self._directoryName)
        return self.__reader


class TermIter:
    """Deprecated thing for countfield"""
    def __init__(self, termEnum, fieldName):
        self._termEnum = termEnum
        self._nextTerm = termEnum.term()
        self._fieldName = fieldName

    def __iter__(self):
        return self

    def next(self):
        if self._nextTerm == None or self._nextTerm.field() != self._fieldName:
            raise StopIteration()
        result, self._nextTerm = self._nextTerm, None
        if self._termEnum.next():
            self._nextTerm = self._termEnum.term()
        return result

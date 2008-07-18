## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
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

from os.path import isdir
from os import makedirs
from PyLucene import IndexReader, IndexWriter, IndexSearcher, StandardAnalyzer, Term, TermQuery, Sort,  StandardTokenizer, StandardFilter, LowerCaseFilter

from meresco.components.lucene.hits import Hits
from meresco.components.lucene.document import IDFIELD
from meresco.framework import Observable, Resource

from bitmatrix import IncNumberMap

class LuceneException(Exception):
    pass

class IncludeStopWordAnalyzer(object):
    def tokenStream(self, fieldName, reader):
        return LowerCaseFilter(StandardFilter(StandardTokenizer(reader)))

def lastUpdateTimeoutToken(method):
    def wrapper(luceneIndexSelf, *args, **kwargs):
        if luceneIndexSelf._lastUpdateTimeoutToken != None:
            luceneIndexSelf._timer.removeTimer(luceneIndexSelf._lastUpdateTimeoutToken)
        try:
            return method(luceneIndexSelf, *args, **kwargs)
        finally:
            luceneIndexSelf._lastUpdateTimeoutToken = luceneIndexSelf._timer.addTimer(1, luceneIndexSelf._lastUpdateTimeout)
    return wrapper

class LuceneIndex(Observable):

    def __init__(self, directoryName, timer, bitwise=False):
        Observable.__init__(self)
        self._bitwise = bitwise
        self._directoryName = directoryName
        self._timer = timer

        self._storedForReopen = {}
        self._storedDeletesForReopen = []
        if not isdir(self._directoryName):
            makedirs(self._directoryName)
        indexExists = IndexReader.indexExists(self._directoryName)
        self._writer = IndexWriter(
            self._directoryName,
            IncludeStopWordAnalyzer(), not indexExists)
        if bitwise:
            self._writer.optimize()                             # create a consistent state
        self._lastUpdateTimeoutToken = None
        self._readerResource = self._openReader()
        self._searcher = self._openSearcher()

        if bitwise:
            self._docIdsAsOriginal = IncNumberMap(self._readerResource.numDocs())
        else:
            self._docIdsAsOriginal = None

    def start(self):
        self.do.indexStarted(self._readerResource)

    def _executeQuery(self, pyLuceneQuery, sortBy=None, sortDescending=None, map=None):
        return Hits(self._searcher, self._readerResource, pyLuceneQuery, self._getPyLuceneSort(sortBy, sortDescending), map)

    def executeQuery(self, pyLuceneQuery, sortBy=None, sortDescending=None):
        return self._executeQuery(pyLuceneQuery, sortBy, sortDescending, self._docIdsAsOriginal)

    def _lastUpdateTimeout(self):
        try:
            self._reopenIndex()
        finally:
            self._lastUpdateTimeoutToken = None

    def _reOpenWriter(self):
        self._writer.close()
        self._writer = IndexWriter(
            self._directoryName,
            IncludeStopWordAnalyzer(), False)

    def _docIdForId(self, id):
        hits = self._executeQuery(TermQuery(Term(IDFIELD, id)))
        oneElementList = hits.bitMatrixRow().asList()
        if len(oneElementList) == 0:
            return None
        assert len(oneElementList) == 1
        return oneElementList[0]

    def getIndexReader(self):
        return self._readerResource

    def _reopenIndex(self):
        self._reOpenWriter()
        #self._readerResource.close()
        self._readerResource = None
        self._readerResource = self._openReader()
        self._searcher.close()
        self._searcher = self._openSearcher()

        if self._bitwise:
            self._doBitwiseExtensions()
        else:
            self.do.indexStarted(self._readerResource)

    def _doBitwiseExtensions(self):
        docIds = []
        for id, documentDict in self._storedForReopen.items():
            fieldAndTermsList = documentDictToFieldsAndTermsList(documentDict)
            docId = self._docIdForId(id)
            if docId != None:
                docIds.append((docId, fieldAndTermsList))
        self._storedForReopen = {}

        for docId in self._storedDeletesForReopen:
            mappedId = self._docIdsAsOriginal.get(docId)
            self.do.deleteDocument(mappedId)
            self._docIdsAsOriginal.delete(docId)
        self._storedDeletesForReopen = []

        if docIds:
            docIds = sorted(docIds)
            for docId, fieldAndTermsList in docIds:
                mappedId = self._docIdsAsOriginal.add(docId)
                self.do.addDocument(mappedId, fieldAndTermsList)

    def _delete(self, anId):
        if self._bitwise:
            docId = self._docIdForId(anId)
            if not docId == None:
                self._storedDeletesForReopen.append(docId)

        self._writer.deleteDocuments(Term(IDFIELD, anId))

    @lastUpdateTimeoutToken
    def delete(self, anId):
        self._delete(anId)

    @lastUpdateTimeoutToken
    def addDocument(self, aDocument):
        self._delete(aDocument.identifier)

        aDocument.validate()
        aDocument.addToIndexWith(self._writer)

        if self._bitwise:
            self._storedForReopen[aDocument.identifier] = aDocument.pokedDict
            if len(self._storedForReopen) >= 250:
                self._reopenIndex()

    def docCount(self):
        return self._readerResource.numDocs()

    def _openReader(self):
        return Resource(IndexReader.open(self._directoryName))

    def _openSearcher(self):
        return IndexSearcher(self._readerResource._subject)

    def _getPyLuceneSort(self, sortBy, sortDescending):
        return sortBy and Sort(sortBy, bool(sortDescending)) or None

    def close(self):
        self._writer.close()
        #self._readerResource.close()
        self._readerResource = None
        self._searcher.close()

    def __del__(self):
        self.close()

    def start(self):
        self._reopenIndex()
        if self._bitwise:
            self.do.indexStarted(self._readerResource)

def documentDictToFieldsAndTermsList(documentDict):
    """Waar dit hoort weten we nog niet zo goed.
    * Let op dat hier ook impliciet in zit dat rechterkanten maar 1 keer voorkomen (set)
    * en dat we hier de strip() doen
    """
    result = {}
    for documentField in documentDict:
        if not documentField.key in result:
            result[documentField.key] = set([])
        result[documentField.key].add(documentField.value.strip())
    return result.items()

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
from PyLucene import IndexReader, IndexWriter, IndexSearcher, StandardAnalyzer, Term, TermQuery, Sort,  StandardTokenizer, StandardFilter, LowerCaseFilter, QueryFilter

from meresco.components.lucene.document import IDFIELD
from meresco.framework import Observable, Resource

from bitmatrix import IncNumberMap, JavaBitSetRow, Row, MappedRow

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

    def __init__(self, directoryName, timer):
        Observable.__init__(self)
        self._directoryName = directoryName
        self._timer = timer
        if not isdir(self._directoryName):
            makedirs(self._directoryName)
        indexExists = IndexReader.indexExists(self._directoryName)
        self._writer = IndexWriter(
            self._directoryName,
            IncludeStopWordAnalyzer(), not indexExists)
        self._lastUpdateTimeoutToken = None
        self._readerResource = self._openReader()
        self._existingFieldNames = self._readerResource.getFieldNames(IndexReader.FieldOption.ALL)
        self._searcher = self._openSearcher()

    def observer_init(self):
        self.do.indexStarted(self._readerResource)

    def bitMatrixRow(self, pyLuceneQuery):
        bits = QueryFilter(pyLuceneQuery).bits(self._readerResource._subject)
        return JavaBitSetRow(bits)

    def executeQuery(self, pyLuceneQuery, start=0, stop=10, sortBy=None, sortDescending=None):
        sortField = self._getPyLuceneSort(sortBy, sortDescending)
        if sortField:
            hits = self._searcher.search(pyLuceneQuery, sortField)
        else:
            hits = self._searcher.search(pyLuceneQuery)
        return len(hits), [hits[i].get(IDFIELD) for i in range(start,min(len(hits),stop))]

    def _lastUpdateTimeout(self):
        try:
            self._reopenIndex()
        finally:
            self._lastUpdateTimeoutToken = None

    def _reOpenWriter(self):
        self._writer.close()
        self._writer = None
        self._writer = IndexWriter(
            self._directoryName,
            IncludeStopWordAnalyzer(), False)

    def _docIdForId(self, id):
        hits = self.executeQuery(TermQuery(Term(IDFIELD, id)))
        if len(hits) == 1:
            return hits[0]
        return None

    def getIndexReader(self):
        return self._readerResource

    def _reopenIndex(self):
        self._reOpenWriter()
        self._readerResource = None
        self._readerResource = self._openReader()
        self._existingFieldNames = self._readerResource.getFieldNames(IndexReader.FieldOption.ALL)
        self._searcher.close()
        self._searcher = None
        self._searcher = self._openSearcher()
        self.do.indexStarted(self._readerResource)

    def _delete(self, anId):
        docId = self._docIdForId(anId)
        self._writer.deleteDocuments(Term(IDFIELD, anId))
        return docId

    @lastUpdateTimeoutToken
    def delete(self, anId):
        return self._delete(anId)

    @lastUpdateTimeoutToken
    def addDocument(self, aDocument):
        self._delete(aDocument.identifier)

        aDocument.validate()
        aDocument.addToIndexWith(self._writer)

    def docCount(self):
        return self._readerResource.numDocs()

    def _openReader(self):
        return Resource(IndexReader.open(self._directoryName))

    def _openSearcher(self):
        return IndexSearcher(self._readerResource._subject)

    def _getPyLuceneSort(self, sortBy, sortDescending):
        if sortBy and sortBy in self._existingFieldNames:
            return Sort(sortBy, bool(sortDescending))
        return None

    def close(self):
        self._writer.close()
        self._readerResource = None
        self._searcher.close()

    def __del__(self):
        self.close()

    def start(self):
        self._reopenIndex()

    def isOptimized(self):
        return self.docCount() == 0 or self._readerResource.isOptimized()

    def getDirectory(self):
        return self._directoryName

    def getMergeFactor(self):
        return self._writer.getMergeFactor()

    def getMaxBufferedDocs(self):
        return self._writer.getMaxBufferedDocs()

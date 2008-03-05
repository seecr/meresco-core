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
from PyLucene import IndexReader, IndexWriter, IndexSearcher, StandardAnalyzer, Term, TermQuery, Sort
from meresco.components.lucene.cqlparsetreetolucenequery import Composer
from meresco.components.lucene.clausecollector import ClauseCollector

from meresco.components.lucene.hits import Hits
from meresco.components.lucene.document import IDFIELD
from meresco.components.statistics import Logger
from meresco.framework import Observable

from bitmatrix import IncNumberMap

class LuceneException(Exception):
    pass


class LuceneIndex(Observable, Logger):

    def __init__(self, directoryName, cqlComposer, timer):
        Observable.__init__(self)
        self._directoryName = directoryName
        self._cqlComposer = cqlComposer
        self._timer = timer
        self._storedForReopen = {}
        self._storedDeletesForReopen = []
        if not isdir(self._directoryName):
            makedirs(self._directoryName)
        indexExists = IndexReader.indexExists(self._directoryName)
        self._writer = IndexWriter(
            self._directoryName,
            StandardAnalyzer(), not indexExists)
        self._writer.optimize()                             # create a consistent state
        self._lastUpdateTimeoutToken = None
        self._reader = self._openReader()
        self._searcher = self._openSearcher()
        self._docIdsAsOriginal = IncNumberMap(self._reader.numDocs())


    def _executeQuery(self, pyLuceneQuery, sortBy=None, sortDescending=None, map=None):
        return Hits(self._searcher, self._reader, pyLuceneQuery, self._getPyLuceneSort(sortBy, sortDescending), map)

    def executeQuery(self, pyLuceneQuery, sortBy=None, sortDescending=None):
        return self._executeQuery(pyLuceneQuery, sortBy, sortDescending, self._docIdsAsOriginal)

    def executeCQL(self, cqlAbstractSyntaxTree, sortBy=None, sortDescending=None):
        ClauseCollector(cqlAbstractSyntaxTree, self.log).visit()
        return self.executeQuery(self._cqlComposer.compose(cqlAbstractSyntaxTree), sortBy, sortDescending)

    def _lastUpdateTimeout(self):
        self._reopenIndex()
        self._lastUpdateTimeoutToken = None

    def _reOpenWriter(self):
        self._writer.close()
        self._writer = IndexWriter(
            self._directoryName,
            StandardAnalyzer(), False)

    def _docIdForId(self, id):
        hits = self._executeQuery(TermQuery(Term(IDFIELD, id)))
        oneElementList = hits.bitMatrixRow().asList()
        if len(oneElementList) == 0:
            return None
        assert len(oneElementList) == 1
        return oneElementList[0]

    def _reopenIndex(self):
        self._reOpenWriter()
        self._reader.close()
        self._reader = self._openReader()
        self._searcher.close()
        self._searcher = self._openSearcher()

        docIds = []
        for id, documentDict in self._storedForReopen.items():
            fieldAndTermsList = documentDictToFieldsAndTermsList(documentDict)
            docId = self._docIdForId(id)
            if docId != None:
                docIds.append((docId, fieldAndTermsList))
        self._storedForReopen = {}

        for docId in self._storedDeletesForReopen:
            self._docIdsAsOriginal.delete(docId)
        self._storedDeletesForReopen = []

        if docIds:
            docIds = sorted(docIds)
            for docId, fieldAndTermsList in docIds:
                mappedId = self._docIdsAsOriginal.add(docId)
                self.do.addDocument(mappedId, fieldAndTermsList)

    def _delete(self, anId):
        docId = self._docIdForId(anId)
        if not docId == None:
            self._storedDeletesForReopen.append(docId)

        self._writer.deleteDocuments(Term(IDFIELD, anId))

    def delete(self, anId):
        if self._lastUpdateTimeoutToken != None:
            self._timer.removeTimer(self._lastUpdateTimeoutToken)
        self._delete(anId)
        self._lastUpdateTimeoutToken = self._timer.addTimer(1, self._lastUpdateTimeout)

    def addDocument(self, aDocument):
        if self._lastUpdateTimeoutToken != None:
            self._timer.removeTimer(self._lastUpdateTimeoutToken)
        self._delete(aDocument.identifier)
        #self._writer.deleteDocuments(Term(IDFIELD, aDocument.identifier))
        aDocument.validate()
        aDocument.addToIndexWith(self._writer)
        self._storedForReopen[aDocument.identifier] = aDocument.pokedDict
        self._lastUpdateTimeoutToken = self._timer.addTimer(1, self._lastUpdateTimeout)

    def docCount(self):
        return self._reader.numDocs()

    def _openReader(self):
        return IndexReader.open(self._directoryName)

    def _openSearcher(self):
        return IndexSearcher(self._reader)

    def _getPyLuceneSort(self, sortBy, sortDescending):
        return sortBy and Sort(sortBy, bool(sortDescending)) or None

    def close(self):
        self._writer.close()
        self._reader.close()
        self._searcher.close()

    def __del__(self):
        self.close()

    def start(self):
        self._reopenIndex()
        self.do.indexStarted(self._reader)


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

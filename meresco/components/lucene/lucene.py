## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) 2007 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2007 Stichting Kennisnet Ict op school.
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

from meresco.components.lucene.cqlparsetreetolucenequery import compose as composeLuceneQuery

from meresco.components.lucene.hits import Hits
from meresco.components.lucene.document import IDFIELD, CONTENTFIELD

class LuceneException(Exception):
    pass

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

    def deleteID(self, anId):
        self._getReader().deleteDocuments(PyLucene.Term(IDFIELD, anId))

    def executeQuery(self, pyLuceneQuery, sortBy=None, sortDescending=None):
        return Hits(self._getSearcher(), pyLuceneQuery, self._getPyLuceneSort(sortBy, sortDescending))

    def executeCQL(self, cqlAbstractSyntaxTree, sortBy=None, sortDescending=None):
        return executeQuery(composeLuceneQuery(cqlAbstractSyntaxTree), sortBy, sortDescending)

    def addToIndex(self, aDocument):
        aDocument.validate()
        aDocument.addToIndexWith(self._getWriter())

    def optimize(self):
        try:
            self._getWriter().optimize()
        finally:
            self.close()

    def docCount(self):
        return self._getReader().numDocs()

    def _getPyLuceneSort(self, sortBy, sortDescending):
        return sortBy and PyLucene.Sort(sortBy, bool(sortDescending)) or None

    def close(self):
        if self.__reader:
            self.__reader.close()
            self.__reader = None
        if self.__searcher:
            self.__searcher.close()
            self.__searcher = None
        if self.__writer:
            self.__writer.close()
            self.__writer = None

    def _getWriter(self, createIndex = False):
        if not self.__writer:
            self.close()
            self.__writer = PyLucene.IndexWriter(self._directoryName, PyLucene.StandardAnalyzer(), createIndex)
        return self.__writer

    def _getSearcher(self):
        if not self.__searcher:
            self.close()
            self.__searcher = PyLucene.IndexSearcher(self._directoryName)
        return self.__searcher

    def _getReader(self):
        if not self.__reader:
            self.close()
            self.__reader = PyLucene.IndexReader.open(self._directoryName)
        return self.__reader

    def __del__(self):
        self.close()


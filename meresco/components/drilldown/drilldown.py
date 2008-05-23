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
#trie version:
#from bitmatrix import BitMatrix, RowTermIndex
from bitmatrix import BitMatrix, Trie
from lucenerawdocsets import LuceneRawDocSets
from time import time

class DrilldownException(Exception):
    pass

class FieldMatrix(object):

    def __init__(self, terms):
        self._matrix = BitMatrix()
        self._trie = Trie()
        self._totalTerms = 0
        self._totalTermLength = 0
        for term, docIds in terms:
            rowNr = self._matrix.addRow(docIds)
            self._addTermToTrie(rowNr, term)

    def addDocument(self, docId, terms):
        for term in terms:
            rowNr = self._trie.getValue(term)
            if rowNr != None:
                self._matrix.appendToRow(rowNr, docId)

            else:
                rowNr = self._matrix.addRow([docId])
                self._addTermToTrie(rowNr, term)

    def _addTermToTrie(self, rowNr, term):
        if type(term) == unicode:
            term = term.encode('utf-8')
        self._trie.add(rowNr, term)
        self._totalTerms += 1
        self._totalTermLength += len(term)


    def deleteDocument(self, docId):
        self._matrix.deleteColumn(docId)

    def drilldown(self, row, maxResults = 0):
        drilldownResults = self._matrix.combinedRowCardinalities(row, maxResults)
        for nr, occurences in drilldownResults:
            yield self._trie.getTerm(nr), occurences

    def sterretje(self, prefix, row, maximumResults=0):
        rowNrs = self._trie.getValues(prefix)
        drilldownResults = self._matrix.sterretje(rowNrs, row, maximumResults)
        for nr, occurences in drilldownResults:
            yield self._trie.getTerm(nr), occurences

class Drilldown(object):

    def __init__(self, drilldownFieldnames):
        self._drilldownFieldnames = drilldownFieldnames
        self._fieldMatrices = {}
        # for supporting the old test only
        self._docSets = self._fieldMatrices

    def loadDocSets(self, rawDocSets):
        for fieldname, terms in rawDocSets:
            self._fieldMatrices[fieldname] = FieldMatrix(terms)

    def addDocument(self, docId, fieldAndTermsList):
        for fieldname, terms in fieldAndTermsList:
            if fieldname in self._drilldownFieldnames:
                self._fieldMatrices[fieldname].addDocument(docId, terms)

    def deleteDocument(self, docId):
        for fieldname in self._drilldownFieldnames:
            self._fieldMatrices[fieldname].deleteDocument(docId)

    def indexStarted(self, indexReader):
        convertor = LuceneRawDocSets(indexReader, self._drilldownFieldnames)
        self.loadDocSets(convertor.getDocSets())

    def drilldown(self, row, drilldownFieldnamesAndMaximumResults):
        for fieldname, maximumResults in drilldownFieldnamesAndMaximumResults:
            if fieldname not in self._drilldownFieldnames:
                raise DrilldownException("No Docset For Field %s, legal docsets: %s" % (fieldname, self._drilldownFieldnames))
            yield fieldname, self._fieldMatrices[fieldname].drilldown(row, maximumResults)

    def sterretje(self, fieldname, prefix, row, maximumResults=0):
        return self._fieldMatrices[fieldname].sterretje(prefix, row, maximumResults)


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

from meresco.components.drilldown.cpp.bitarray import DenseBitArray, SparseBitArray

DENSE_SPARSE_BREAKING_POINT = 32

def createDocSet(docs, length):
    docList = list(docs)
    cardinality = len(docList)
    if cardinality * DENSE_SPARSE_BREAKING_POINT > length:
        result = DenseBitArray(length)
    result = SparseBitArray(cardinality)
    for doc in docList:
        result.set(doc)
    return result

class DrilldownException(Exception):
    pass

class Drilldown(object):

    def __init__(self, drilldownFieldNames):
        self._drilldownFieldnames = drilldownFieldNames

    def drilldown(self, docIds, drilldownFieldnamesAndMaximumResults):
        drilldownResults = []
        queryDocSet = self._docSetForQueryResult(docIds)
        for fieldName, maximumResults in drilldownFieldnamesAndMaximumResults:
            drilldownResults.append((fieldName,
                    self._processField(fieldName, queryDocSet, maximumResults)))
        return drilldownResults

    def loadDocSets(self, rawDocSets, docCount):
        def cmpCardinality(left, right):
            return cmp(left[1].cardinality(), right[1].cardinality())

        self._numDocsInIndex = docCount

        self._docSets = {}
        for fieldname, terms in rawDocSets:
            self._docSets[fieldname] = []
            for term, docIds in terms:
                self._docSets[fieldname].append((term, createDocSet(docIds, self._numDocsInIndex)))
            self._docSets[fieldname].sort(cmpCardinality)

    def _docSetForQueryResult(self, docIds):
        sortedDocs = sorted(docIds)
        return createDocSet(sortedDocs, self._numDocsInIndex)

    def _processField(self, fieldName, drilldownBitArray = None, maximumResults = 0):
        #sort on cardinality, truncate with maximumResults and return smallest cardinality
        #if no limit is present return 0
        def sortAndTruncateAndGetMinValueInResult(resultList):
            if maximumResults:
                resultList.sort(lambda (termL, countL), (termR, countR): cmp(countR, countL))
                del resultList[maximumResults:]
                if len(resultList) == maximumResults:
                    return resultList[-1][1] #Cardinality of last element
            return 0

        if not self._docSets.has_key(fieldName):
            raise DrilldownException("No Docset For Field %s, legal docsets: %s" % (fieldName, self._docSets.keys()))
        result = []

        if not drilldownBitArray:
            for term, docSet in self._docSets[fieldName]:
                result.append((term, docSet.cardinality()))
        else: #Use drilldownBitArray << This branch is the HOTSPOT >>
            minValueInResult = 0
            for term, docSet in self._docSets[fieldName]:
                if docSet.cardinality() < minValueInResult:
                    break

                cardinality = docSet.combinedCardinality(drilldownBitArray)

                if cardinality > minValueInResult:
                    result.append((term, cardinality))
                    minValueInResult = sortAndTruncateAndGetMinValueInResult(result)
        return result

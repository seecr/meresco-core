from itertools import takewhile, dropwhile

class SegmentInfo(object):
    def __init__(self, length, offset):
        self.length = length
        self.offset = offset
    def __repr__(self):
        return '%d@%d' % (self.length, self.offset)

class LuceneDocIdTracker(object):
    """
        This class tracks docids for Lucene version 2.2.0
                                                    =====
    """
    def __init__(self, mergeFactor):
        self._mergeFactor = mergeFactor
        self._nextDocId = 0
        self._docIds = []
        self._segmentInfo = []
        self._ramSegmentsInfo = []

    def next(self):
        self._ramSegmentsInfo.append(SegmentInfo(1, len(self._docIds)))
        self._docIds.append(self._nextDocId)
        self._nextDocId += 1
        if len(self._ramSegmentsInfo) >= self._mergeFactor:
            self._flushRamSegments()
        return self._nextDocId - 1

    def _flushRamSegments(self):
        if len(self._ramSegmentsInfo) > 0:
            self._merge(self._ramSegmentsInfo, self._ramSegmentsInfo[0].offset, 0, self._mergeFactor)
            self._segmentInfo.append(self._ramSegmentsInfo[0])
            self._ramSegmentsInfo = []
            self._maybeMerge(self._segmentInfo, lower = 0, upper = self._mergeFactor)

    def _maybeMerge(self, segments, lower, upper):
        reversedSegments = reversed(segments)
        worthySegments = list(takewhile(lambda si: si.length <= upper,
            dropwhile(lambda si: not lower < si.length <= upper , reversedSegments)))
        nrOfWorthySegments = len(worthySegments)
        if nrOfWorthySegments == self._mergeFactor:
            self._merge(segments, worthySegments[-1].offset, lower, upper)

    def _merge(self, segments, newOffset, lower, upper):
        merged = [docid for docid in self._docIds[newOffset:] if docid >= 0]
        del self._docIds[newOffset:]
        self._docIds.extend(merged)
        newLength = len(merged)
        si = SegmentInfo(newLength, newOffset)
        del segments[-self._mergeFactor:]
        segments.append(si)
        if newLength > upper:
            self._maybeMerge(segments, lower=upper, upper=upper*self._mergeFactor)

    def deleteDocId(self, docid):
        assert self._docIds[docid] != -1
        removedUDocID = self._docIds[docid]
        self._docIds[docid] = -1
        self._flushRamSegments()
        return removedUDocID

    def map(self, docids):
        return (self._docIds[docid] for docid in docids)

    def flush(self):
        self._flushRamSegments()

class LuceneDocIdTrackerDecorator(object):

    def __init__(self, luceneIndex):
        assert luceneIndex.isOptimized(), 'index must be optimized'
        mergeFactor = luceneIndex.getMergeFactor()
        maxBufferedDocs = luceneIndex.getMaxBufferedDocs()
        assert mergeFactor == maxBufferedDocs, 'mergeFactor != maxBufferedDocs'
        self._lucene = luceneIndex
        self._tracker = LuceneDocIdTracker(mergeFactor)

    def addDocument(self, doc):
        self._lucene.addDocument(doc)
        return self._tracker.next()

    def delete(self, identifier):
        docId = self._lucene.delete(identifier)
        return self._tracker.deleteDocId(docId)

    def executeQuery(self, *args, **kwargs):
        hits = self._lucene.executeQuery(*args, **kwargs)
        return HitsDecorator(hits, self._tracker._docIds)

    def getDocSets(self, fieldNames):
        pass

class HitsDecorator(object):

    def __init__(self, hits, docidsMap):
        self._hits = hits
        self._docIdsMap = docidsMap

    def bitMatrixRow(self):
        return self._hits.bitMatrixRow(self._docIdsMap)


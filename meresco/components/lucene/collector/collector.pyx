
cdef extern int * createArray(int size)
cdef extern void freeArray(int *)
cdef extern int addDoc(int *, int, int)


cdef class Collector:
    cdef int *_scoreDocs
    cdef int _offset

    def __init__(self, int maxRows):
        self._offset = 0;
        self._scoreDocs = createArray(maxRows)

    def __dealloc__(self):
        freeArray(self._scoreDocs)

    def collect(self, int doc, float score):
        self._offset = addDoc(self._scoreDocs, self._offset, doc)

    def getDocs(self):
        result = []
        for i from 0 <= i < self._offset:
            result.append(self._scoreDocs[i])
        return result

def getScoreDocs(int maxDocs, weight, searcher):
    collector = Collector(maxDocs)
    searcher.search(weight, None, collector)
    return collector.getDocs()

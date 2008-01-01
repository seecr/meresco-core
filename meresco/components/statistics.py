import cPickle as pickle
from os import rename, remove
from os.path import isfile, join
from inspect import currentframe
from time import time
from meresco.framework import Observable, compose

def combinations(head, tail):
    for value in head:
        if not tail:
            yield (value,)
        else:
            for trailer in combinations(tail[0], tail[1:]):
                yield (value,) + trailer

class Logger(object):
    def log(self, **kwargs):
        frame = currentframe().f_back
        while frame:
            if "__log__" in frame.f_locals:
                var = frame.f_locals["__log__"]
                for key, value in kwargs.items():
                    if not key in var:
                        var[key] = []
                    var[key].append(value)
                return
            frame = frame.f_back

class Statistics(Observable):
    def __init__(self, path, keys, snapshotInterval=3600):
        Observable.__init__(self)
        self._path = path
        self._snapshotFilename = join(self._path, 'snapshot')
        self._txlogFileName = join(self._path, 'txlog')
        self._txlogFile = None
        self._keys = keys
        self._snapshotInterval = snapshotInterval
        self._lastSnapshot = 0
        self._data = {}
        self._readState()

    def __del__(self):
        if self._txlogFile and not self._txlogFile.closed:
            self._txlogFile.close()

    def unknown(self, message, *args, **kwargs):
        __log__ = {} # to be found on the call stack by Logger
        responses = self.all.unknown(message, *args, **kwargs)
        for response in responses:
            yield response
        self._process(__log__)
        self._snapshotIfNeeded()

    def listKeys(self):
        return self._keys

    def get(self, t0, t1, key):
        if key not in self._keys:
            raise KeyError('%s not in %s' % (key, self._keys))
        result = {}
        for t, data in self._data.items():
            if int(t) >= t0 and int(t) <= t1:
                if key in data:
                    for term, count in data[key].items():
                        if term in result:
                            result[term] += count
                        else:
                            result[term] = count
        return result

    def _clock(self):
        return int(time())

    def _process(self, logLine):
        t = self._clock()
        self._logTx(t, logLine)
        for key in self._keys:
            self._updateData(t, key, logLine)

    def _updateData(self, t, statistic, logLine):
        if not t in self._data:
            self._data[t] = {}
        data = self._data[t]
        if statistic not in data:
            data[statistic] = {}
        fieldValuesList = tuple(logLine.get(fieldName, ["#undefined"]) for fieldName in statistic)
        fieldValuesCombos = combinations(fieldValuesList[0], fieldValuesList[1:])
        for fieldValues in fieldValuesCombos:
            if not fieldValues in data[statistic]:
                data[statistic][fieldValues] = 0
            data[statistic][fieldValues] += 1

    def _readState(self):
        if isfile(self._snapshotFilename + ".writing"):
            self._rollbackSnapshot()
        if isfile(self._snapshotFilename + ".writing.done"):
            self._commitSnapshot()
        if isfile(self._snapshotFilename):
            self._initializeFromSnapshot()
        if isfile(self._txlogFileName):
            self._initializeFromTxLog()
        self._lastSnapshot = self._clock()

    def _writeSnapshot(self):
        self._prepareSnapshot()
        self._commitSnapshot()
        self._lastSnapshot = self._clock()

    def _prepareSnapshot(self):
        snapshotFile = open(self._snapshotFilename + '.writing', 'wb')
        try:
            pickle.dump(self._data, snapshotFile)
        finally:
            snapshotFile.close()
        rename(self._snapshotFilename + '.writing', self._snapshotFilename + '.writing.done')

    def _commitSnapshot(self):
        if isfile(self._txlogFileName):
            remove(self._txlogFileName)
            self.__txlog = None
        rename(self._snapshotFilename + '.writing.done', self._snapshotFilename)

    def _rollbackSnapshot(self):
        remove(self._snapshotFilename + ".writing")

    def _initializeFromTxLog(self):
        txfile = open(self._txlogFileName, 'r')
        try:
            for logLine in txfile:
                t, dictString = logLine.strip().split('\t')
                for key in self._keys:
                    self._updateData(t, key, eval(dictString))
        finally:
            txfile.close()

    def _initializeFromSnapshot(self):
        snapshotFile = open(self._snapshotFilename, 'rb')
        try:
            self._data = pickle.load(snapshotFile)
        finally:
            snapshotFile.close()

    def _txlog(self):
        if not self._txlogFile:
            self._txlogFile = open(self._txlogFileName, 'a')
        return self._txlogFile

    def _logTx(self, t, aDictionary):
        line = str(t) + '\t' + repr(aDictionary)
        fp = self._txlog()
        fp.write(line + "\n")
        fp.flush()

    def _snapshotIfNeeded(self):
        if self._clock() >= self._lastSnapshot + self._snapshotInterval:
            self._writeSnapshot()

class AggregatorNode(object):
    def __init__(self):
        self._values = []
        self._children = {}

    def add(self, l, data):
        if len(l) == 0:
            self._values.append(data)
        else:
            head, tail = l[0], l[1:]
            if not head in self._children:
                self._children[head] = AggregatorNode()
            self._children[head].add(tail, data)

    def get(self, l):
        if len(l) == 0:
            for value in self._values:
                yield value
            for child in self._children.values():
                yield child.get(l)
            raise StopIteration
        head, tail = l[0], l[1:]
        if not head in self._children:
            raise StopIteration
        yield self._children[head].get(tail)


class Aggregator(object):

    def __init__(self):
        self._root = AggregatorNode()

    def add(self, data):
        self._root.add(self._clock(), data)

    def get(self, fromTime):
        return compose(self._root.get(fromTime))

    def _clock(self):
        return gmtime()[:6]

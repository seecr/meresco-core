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

class Top100s(object):
    def __init__(self, data=None):
        if not data:
            data = {}
        self._data = data

    def inc(self, statisticId, occurrence, count=1):
        if not statisticId in self._data:
            self._data[statisticId] = {}
        if not occurrence in self._data[statisticId]:
            self._data[statisticId][occurrence] = 0
        self._data[statisticId][occurrence] += count

    def getTop100(self, statisticId):
        return self._data.get(statisticId, {}).items()

    def statisticIds(self):
        return self._data.keys()

    def __eq__(self, other):
        return other.__class__ == self.__class__ and other._data == self._data

class DataFactory(object):

    def doInit(self):
        return Data()

    def doAdd(self, data, (statistic, fieldValues)):
        data.inc(statistic, fieldValues)

    def doExtend(self, data0, data1):
        for statistic in data1.keys():
            for term, count in data1.get(statistic):
                data0.inc(statistic, term, count)

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
                for term, count in data.getTop100(key):
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
            self._data[t] = Top100s()
        data = self._data[t]
        fieldValuesList = tuple(logLine.get(fieldName, ["#undefined"]) for fieldName in statistic)
        fieldValuesCombos = combinations(fieldValuesList[0], fieldValuesList[1:])
        for fieldValues in fieldValuesCombos:
            data.inc(statistic, fieldValues)

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

class AggregatorException(Exception):
    pass

class AggregatorNode(object):
    def __init__(self, xxxFactory, aggregationQueues):
        self._xxxFactory = xxxFactory
        self._aggregationQueues = aggregationQueues
        self._values = self._xxxFactory.doInit()
        self._children = {}
        self._aggregated = False

    def _aggregate(self):
        if self._aggregated:
            return
        for nr, child in self._children.items():
            child._aggregate()
            self._xxxFactory.doExtend(self._values, child._values)
        self._aggregated = True

    def add(self, time, data, depth):
        if len(time) == 0:
            self._xxxFactory.doAdd(self._values, data)
        else:
            head, tail = time[0], time[1:]
            if not head in self._children:
                self._children[head] = AggregatorNode(self._xxxFactory, self._aggregationQueues)
            self._children[head].add(tail, data, depth + 1)
            current = self._children[head]
            q = self._aggregationQueues[depth]
            if current not in q:
                q.append(current)
            if len(q) >= 3:
                toDo = q[0]
                q.remove(toDo)
                toDo._aggregate()

    def get(self, result, fromTime, untilTime):
        BEGIN = (0, 0, 0, 0, 0, 0)
        END = (9999, 9999, 9999, 9999, 9999, 9999)

        assert len(fromTime) == len(untilTime), (fromTime, untilTime)
        if len(fromTime) == 0:
            self._xxxFactory.doExtend(result, self._values)
            if not self._aggregated:
                for digit, child in self._children.items():
                    child.get(result, fromTime, untilTime)
            return result

        if self._aggregated:
            raise AggregatorException('too precise')

        fromHead, fromTail = fromTime[0], fromTime[1:]
        untilHead, untilTail = untilTime[0], untilTime[1:]
        for digit, child in self._children.items():
            if digit >= fromHead and \
                ((fromTail and digit <= untilHead) or (not fromTail and digit < untilHead)):
                if digit == fromHead:
                    useFrom = fromTail
                else: #digit > fromHead
                    if not fromTail:
                        useFrom = fromTail
                    else:
                        useFrom = BEGIN[-1 * len(fromTail):]
                if digit == untilHead:
                    useUntil = untilTail
                else: #digit < untilHead
                    if not untilTail:
                        useUntil = untilTail
                    else:
                        useUntil = END[-1 * len(untilTail):]
                child.get(result, useFrom, useUntil)

        return result


    def oldget(self, result, fromTime, untilTime):
        if len(time) == 0:
            self._xxxFactory.doExtend(result, self._values)
            if not self._aggregated:
                for nr, child in self._children.items():
                    child.get(result, time)
            return result
        if self._aggregated:
            raise AggregatorException('too precise')
        head, tail = time[0], time[1:]
        if not head in self._children:
            return result
        return self._children[head].get(result, tail)

class Aggregator(object):

    def __init__(self, xxxFactory):
        self._aggregationQueues = [[], [], [], [], [], [], []]
        self._root = AggregatorNode(xxxFactory, self._aggregationQueues)
        self._xxxFactory = xxxFactory

    def add(self, data):
        self._addAt(gmtime()[:6], data)

    def _addAt(self, time, data):
        self._root.add(time, data, 0)

    def get(self, fromTime, untilTime=None):
        if untilTime == None:
            untilTime = list(fromTime[:])
            untilTime[-1] += 1
            untilTime = tuple(untilTime)
        return self._root.get(self._xxxFactory.doInit(), fromTime, untilTime)

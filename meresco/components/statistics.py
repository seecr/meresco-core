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
import cPickle as pickle
from os import rename, remove
from os.path import isfile, join
from inspect import currentframe
from time import mktime, gmtime
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
        self._data[statisticId] = dict(self.getTop100(statisticId))

    def getTop100(self, statisticId):
        return sorted(self._data.get(statisticId, {}).items())[:100]

    def statisticIds(self):
        return self._data.keys()

    def __eq__(self, other):
        return other.__class__ == self.__class__ and other._data == self._data

class Top100sFactory(object):
    def doInit(self):
        return Top100s()

    def doAdd(self, top100s, (statistic, fieldValues)):
        top100s.inc(statistic, fieldValues)

    def doExtend(self, left, right):
        for id in right.statisticIds():
            for occurrence, count in right.getTop100(id):
                left.inc(id, occurrence, count)

class Statistics(Observable):
    def __init__(self, path, keys, snapshotInterval=3600):
        Observable.__init__(self)
        self._path = path
        self._snapshotFilename = join(self._path, 'snapshot')
        self._txlogFileName = join(self._path, 'txlog')
        self._txlogFile = None
        self._keys = keys
        self._snapshotInterval = snapshotInterval
        self._lastSnapshot = (1970, 1, 1, 0, 0, 0)
        self._data = Aggregator(Top100sFactory())
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

    def get(self, statisticId, t0=None, t1=None):
        if not t0:
            t0 = ()
        if statisticId not in self._keys:
            raise KeyError('%s not in %s' % (statisticId, self._keys))
        return dict(self._data.get(t0, t1).getTop100(statisticId))
        #opruimen: dict staat hier even voor de tests

    def _clock(self):
        return gmtime()[:6]

    def _process(self, logLine):
        t = self._clock()
        self._logTx(t, logLine)
        for key in self._keys:
            self._updateData(t, key, logLine)

    def _updateData(self, t, statistic, logLine):
        fieldValuesList = []
        for fieldName in statistic:
            if not fieldName in logLine:
                return
            fieldValuesList.append(logLine[fieldName])
        fieldValuesCombos = combinations(fieldValuesList[0], fieldValuesList[1:])
        for fieldValues in fieldValuesCombos:
            self._data._addAt(t, (statistic, fieldValues))

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
                    self._updateData(eval(t), key, eval(dictString))
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

    def _tm(self, sixTuple):
        return mktime(sixTuple + (0,0,0))

    def _snapshotIfNeeded(self):
        if self._tm(self._clock()) >= self._tm(self._lastSnapshot) + self._snapshotInterval:
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
        self._children = {}
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
        if not fromTime and not untilTime:
            self._xxxFactory.doExtend(result, self._values)
            if not self._aggregated:
                for digit, child in self._children.items():
                    child.get(result, [], [])
            return result

        if self._aggregated:
            raise AggregatorException('too precise')

        for digit, child in self._children.items():
            left = fromTime
            if fromTime:
                if digit < fromTime[0]:
                    continue
                elif digit == fromTime[0]:
                    left = fromTime[1:]
                else:
                    left = []

            right = untilTime
            if untilTime:
                if digit > untilTime[0]:
                    continue
                elif digit == untilTime[0]:
                    right = untilTime[1:]
                else:
                    right = []

            child.get(result, left, right)
        return result

    def __resssssspr__(self):
        return "\nAggregatorNode Children:\n%s \nvalues:%s\n" % (self._children, self._values)

class Aggregator(object):

    def __init__(self, xxxFactory):
        self._aggregationQueues = [[], [], [], [], [], [], []]
        self._root = AggregatorNode(xxxFactory, self._aggregationQueues)
        self._xxxFactory = xxxFactory

    def add(self, data):
        self._addAt(gmtime()[:6], data)

    def _addAt(self, time, data):
        self._root.add(time, data, 0)

    def get(self, fromTime=(), untilTime=()):
        return self._root.get(self._xxxFactory.doInit(), fromTime, untilTime)

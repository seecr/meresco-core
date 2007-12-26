import cPickle as pickle
from os import rename, remove
from os.path import isfile, join
from inspect import currentframe
from time import time
from meresco.framework import Observable

class Logger(object):
    def log(self, **kwargs):
        frame = currentframe().f_back
        while frame:
            if "__log__" in frame.f_locals:
                frame.f_locals["__log__"].update(kwargs)
                return
            frame = frame.f_back

class Statistics(Observable):
    def __init__(self, path, keys):
        Observable.__init__(self)
        self._path = path
        self._snapshotFilename = join(self._path, 'snapshot')
        self._txlogFileName = join(self._path, 'txlog')
        self._txlogFile = None
        self._keys = keys
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

    def get(self, t0, t1, key):
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

    def show(self):
        yield "<statistics>"
        for key in self._keys:
            yield "<statistic>"
            yield "<query>"
            for keyPart in key:
                yield "<fieldName>%s</fieldName>" % keyPart
            yield "</query>"
            from time import time
            data = self.get(0, time() + 1, key)
            for value, count in data.items():
                yield "<result>"
                for keyPart in value:
                    yield "<fieldValue>%s</fieldValue>" % keyPart
                yield "<count>%s</count>" % count
                yield "</result>"
            yield "</statistic>"
        yield "</statistics>"

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
        fieldValues = tuple([logLine.get(fieldName, "#undefined") for fieldName in statistic])
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

    def _writeSnapshot(self):
        self._prepareSnapshot()
        self._commitSnapshot()

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
                t, logData = logLine.split('\t', 1)
                data = self._stringToDict(logData.strip())
                for key in self._keys:
                    self._updateData(t, key, data)
        finally:
            txfile.close()

    def _initializeFromSnapshot(self):
        snapshotFile = open(self._snapshotFilename, 'rb')
        try:
            self._data = pickle.load(snapshotFile)
        finally:
            snapshotFile.close()

    def _stringToDict(self, aString):
        return dict((key,value)
            for key,value in (part.split(':',1)
                for part in aString.split('\t') if part))

    def _dictToString(self, aDictionary):
        return '\t'.join(key+':'+value
            for key,value in aDictionary.items() if key and value)

    def _txlog(self):
        if not self._txlogFile:
            self._txlogFile = open(self._txlogFileName, 'a')
        return self._txlogFile

    def _logTx(self, t, aDictionary):
        line = str(t) + '\t' + self._dictToString(aDictionary)
        fp = self._txlog()
        fp.write(line + "\n")
        fp.flush()


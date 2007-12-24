import cPickle as pickle
from os import rename, remove
from os.path import isfile, join

from meresco.framework import Observable

class Statistics(Observable):
    def __init__(self, path, keys):
        Observable.__init__(self)
        self._path = path
        self._snapshotFilename = join(self._path, 'snapshot')
        self._txlogFilename = join(self._path, 'txlog')
        self._txlogFileFP = None
        self._keys = keys
        self._data = {}
        self._readState()

    def unknown(self, message, *args, **kwargs):
        __log__ = {}
        stuffs = self.all.unknown(message, *args, **kwargs)
        for stuff in stuffs:
            yield stuff
        self._process(__log__)

    def show(self):
        yield "<statistics>"
        for key in self._keys:
            yield "<statistic>"
            yield "<query>"
            for keyPart in key:
                yield "<fieldName>%s</fieldName>" % keyPart
            yield "</query>"
            data = self._data[key]
            for value, count in data.items():
                yield "<result>"
                for keyPart in value:
                    yield "<fieldValue>%s</fieldValue>" % keyPart
                yield "<count>%s</count>" % count
                yield "</result>"
            yield "</statistic>"
        yield "</statistics>"

    def _process(self, logLine):
        self._logToFile(logLine)
        for key in self._keys:
            self._updateData(key, logLine)

    def _readState(self):
        if isfile(self._snapshotFilename + ".writing"):
            self._writeSnapshotRollback()
        if isfile(self._snapshotFilename + ".writing.done"):
            self._writeSnapshotCommit()
        if isfile(self._snapshotFilename):
            self._initializeFromSnapshot()
        if isfile(self._txlogFilename):
            self._initializeFromFile()

    def _writeSnapshot(self):
        self._writeSnapshotPrepare()
        self._writeSnapshotCommit()

    def _writeSnapshotPrepare(self):
        snapshotFile = open(self._snapshotFilename + '.writing', 'wb')
        try:
            pickle.dump(self._data, snapshotFile)
        finally:
            snapshotFile.close()
        rename(self._snapshotFilename + '.writing', self._snapshotFilename + '.writing.done')

    def _writeSnapshotCommit(self):
        if isfile(self._txlogFilename):
            remove(self._txlogFilename)
            self._txlogFileFP = None
        rename(self._snapshotFilename + '.writing.done', self._snapshotFilename)

    def _writeSnapshotRollback(self):
        remove(self._snapshotFilename + ".writing")

    def _initializeFromFile(self):
        fp = open(self._txlogFilename)

        try:
            data = (self._stringToDict(line.strip()) for line in fp.readlines())
            for logLine in data:
                for key in self._keys:
                    self._updateData(key, logLine)
        finally:
            fp.close()

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

    def _updateData(self, statistic, logLine):
        if statistic not in self._data:
            self._data[statistic] = {}
        fieldValues = tuple([logLine.get(fieldName, "#undefined") for fieldName in statistic])
        if not fieldValues in self._data[statistic]:
            self._data[statistic][fieldValues] = 0
        self._data[statistic][fieldValues] += 1

    def _txlogFile(self):
        if not self._txlogFileFP:
            self._txlogFileFP = open(self._txlogFilename, 'a')
        return self._txlogFileFP

    def _logToFile(self, aDictionary):
        line = self._dictToString(aDictionary)
        fp = self._txlogFile()
        fp.write(line + "\n")
        fp.flush()


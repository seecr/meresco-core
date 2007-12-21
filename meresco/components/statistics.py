
from os.path import isfile

from meresco.framework import Observable

class Statistics(Observable):
    def __init__(self, dataFilename, keys):
        Observable.__init__(self)
        self._dataFilename = dataFilename
        self._keys = keys
        self._data = {}

        if isfile(self._dataFilename):
            self._initializeFromFile()

    def unknown(self, message, *args, **kwargs):
        logLine = {}
        kwargs['logLine'] = logLine
        stuffs = self.all.unknown(message, *args, **kwargs)
        for stuff in stuffs:
            yield stuff
        self._process(logLine)

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

    def _initializeFromFile(self):
        fp = open(self._dataFilename)

        try:
            data = (self._stringToDict(line.strip()) for line in fp.readlines())
            for logLine in data:
                for key in self._keys:
                    self._updateData(key, logLine)
        finally:
            fp.close()

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

    def _logToFile(self, aDictionary):
        line = self._dictToString(aDictionary)
        fp = open(self._dataFilename, 'a')
        try:
            fp.write(line + "\n")
        finally:
            fp.close()
from os.path import isfile

class Statistics(object):
    def __init__(self, dataFilename, keys):
        self._dataFilename = dataFilename
        self._keys = keys
        self._data = {}

        if isfile(self._dataFilename):
            self._initializeFromFile()

    def _initializeFromFile(self):
        fp = open(self._dataFilename)

        try:
            data = (self._stringToDict(line.strip()) for line in fp.readlines())
            for item in data:
                self.process(item)
        finally:
            fp.close()

    def _stringToDict(self, aString):
        return dict((key,value)
            for key,value in (part.split(':',1)
                for part in aString.split('\t') if part))

    def _dictToString(self, aDictionary):
        return '\t'.join(key+':'+value
            for key,value in aDictionary.items() if key and value)

    def process(self, data):
        self._logToFile(data)
        for key in self._keys:
            self._updateData(key, data)

    def _updateData(self, key, data):
        if key not in self._data:
            self._data[key] = {}

        valueKey = tuple([data[part] for part in key])
        if not valueKey in self._data[key]:
            self._data[key][valueKey] = 0
        self._data[key][valueKey] += 1

    def _logToFile(self, aDictionary):
        line = self._dictToString(aDictionary)
        fp = open(self._dataFilename, 'a')
        try:
            fp.write(line + "\n")
        finally:
            fp.close()
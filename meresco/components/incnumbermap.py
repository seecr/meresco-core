

class IncNumberMapException(Exception):
    pass

class IncNumberMap(object):
    def __init__(self):
        self._map = []
        self._number = 0

    def add(self, docId):
        if docId != len(self._map):
            raise IncNumberMapException('Re adding not allowed')
        self._map.append(self._number)
        self._number += 1
        return self._number - 1

    def get(self, docId):
        if docId >= len(self._map):
            raise IncNumberMapException('Index Out Of Range')
        return self._map[docId]

    def deleteAndCollapse(self, docId):
        self._map.remove(self._map[docId]) #l.removeElementAt(docId)

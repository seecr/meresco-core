

class IncNumberMapException(Exception):
    pass

class IncNumberMap(object):
    def __init__(self, length):
        self._map = range(length)
        self._number = length

    def add(self, docId):
        if docId != len(self._map):
            raise IncNumberMapException('Re adding not allowed')
        self._map.append(self._number)
        self._number += 1
        return self._number - 1

    def get(self, docId):
        if docId >= len(self._map):
            raise IncNumberMapException('Index Out Of Range')
        result = self._map[docId]
        if result == None:
            raise IncNumberMapException("docId %s already deleted" % docId)

        return result

    def delete(self, docId):
        self._map[docId] = None

    def collapse(self, nrOfFilledHoles):
        i = len(self._map) - 1
        while nrOfFilledHoles:
            if i == -1:
                raise IncNumberMapException("Cannot collapse any further")
            if self._map[i] == None:
                self._map[i] = "dead"
                self._map.remove("dead")
                nrOfFilledHoles += -1
            i += -1

    def deleteAndCollapse(self, docId):
        self._map.remove(self._map[docId]) #l.removeElementAt(docId)

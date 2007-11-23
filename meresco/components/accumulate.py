from meresco.framework import Observable
from meresco.components.dictionary import DocumentDict


def getIdentifier(*args, **kwargs):
    return args[0]

def emptyGenerator():
    if False:
        yield None

class Accumulate(Observable):

    def __init__(self, message, combine, getIdentifier=getIdentifier):
        Observable.__init__(self)
        self._reset()
        self._message = message
        self._getIdentifier = getIdentifier
        self._combine = combine

    def _reset(self):
        self._identifier = None
        self._collection = []

    def finish(self):
        if self._identifier:
            return self._send()
        return emptyGenerator()

    def _send(self):
        args, kwargs = self._combine(self._collection)
        self._reset()
        return self.all.unknown(self._message, *args, **kwargs)

    def _collect(self, *args, **kwargs):
        self._collection.append((args, kwargs))

    def unknown(self, message, *args, **kwargs):
        if message == self._message:
            result = emptyGenerator()
            identifier = self._getIdentifier(*args, **kwargs)
            if self._identifier and self._identifier != identifier:
                result = self._send()
            self._identifier = identifier
            self._collect(*args, **kwargs)
            return result
        else:
            return self.all.unknown(message, *args, ** kwargs)
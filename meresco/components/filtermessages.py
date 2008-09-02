
from meresco.framework import Observable

class FilterMessages(Observable):
    def __init__(self, allowed=[], disallowed=[]):
        Observable.__init__(self)
        assert len(allowed) == 0 or len(disallowed) == 0, 'Use disallowed or allowed'
        if allowed:
            self._allowedMessage = lambda message: message in allowed
        else:
            self._allowedMessage = lambda message: message not in disallowed

    def unknown(self, message, *args, **kwargs):
        if self._allowedMessage(message):
            return self.all.unknown(message, *args, **kwargs)
from meresco.framework import Transparant

def _emptyGenerator():
    if False:
        yield None

class IpFilter(Transparant):

    def __init__(self, whitelist):
        Transparant.__init__(self)
        self._whitelist = whitelist

    def handleRequest(self, *args, **kwargs):
        if kwargs.get("Client", ["",])[0] in self._whitelist:
            return self.all.handleRequest(*args, **kwargs)
        return _emptyGenerator()
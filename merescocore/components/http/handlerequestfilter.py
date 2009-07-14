
from merescocore.framework import Observable

class HandleRequestFilter(Observable):
    def __init__(self, filterMethod):
        Observable.__init__(self)
        self._filter = filterMethod
    
    def handleRequest(self, **kwargs):
        if self._filter(**kwargs):
            return self.all.handleRequest(**kwargs)
        return (f for f in [])

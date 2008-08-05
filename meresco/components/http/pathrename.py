
from meresco.framework import Transparant
class PathRename(Transparant):
    def __init__(self, rename):
        Transparant.__init__(self)
        self._rename = rename

    def handleRequest(self, path, *args, **kwargs):
        yield self.all.handleRequest(path=self._rename(path), *args, **kwargs)
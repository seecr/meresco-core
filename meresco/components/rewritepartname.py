from meresco.framework import Transparant

class RewritePartname(Transparant):

    def __init__(self, partname):
        Transparant.__init__(self)
        self._partname = partname

    def add(self, id, partname, document):
        self.do.add(id, self._partname, document)

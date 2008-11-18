from meresco.framework import Transparant

class OaiSetSelect(Transparant):
    def __init__(self, setsList):
        Transparant.__init__(self)
        self._setsList = setsList

    def oaiSelect(self, sets=[], *args, **kwargs):
        if not sets:
            sets = []
        sets += self._setsList
        yield self.all.oaiSelect(sets=sets, *args, **kwargs)
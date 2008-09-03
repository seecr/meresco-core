
from meresco.framework import Observable
from cqlparser import parseString

class String2CQL(Observable):
    def executeCQLString(self, cqlString, *args, **kwargs):
        return self.any.executeCQL(parseString(cqlString), *args, **kwargs)
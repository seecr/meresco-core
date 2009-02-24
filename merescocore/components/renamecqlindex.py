
from cqlparser import CqlIdentityVisitor

class RenameCqlIndex(object):
    def __init__(self, fieldRename):
        self._fieldRename = fieldRename

    def __call__(self, cqlAst):
        return _CqlIndexChangeVisitor(self._fieldRename, cqlAst).visit()
        
class _CqlIndexChangeVisitor(CqlIdentityVisitor):
    def __init__(self, fieldRename, root):
        CqlIdentityVisitor.__init__(self, root)
        self._fieldRename = fieldRename
        
    def visitINDEX(self, node):
        assert len(node.children()) == 1
        myterm = node.children()[0]
        return node.__class__(myterm.__class__(self._fieldRename(myterm.children()[0])))


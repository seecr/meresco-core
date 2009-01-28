
from xmlpump import Converter
from cqlparser.cqlparser import CQLAbstractSyntaxNode
from cqlparser import CqlIdentityVisitor

class CQLConversion(Converter):
    def __init__(self, fieldRename):
        Converter.__init__(self)
        self._fieldRename = fieldRename

    def _canConvert(self, anObject):
        return isinstance(anObject, CQLAbstractSyntaxNode)

    def _convert(self, cqlAst):
        class CqlIndexChangeVisitor(CqlIdentityVisitor):
            def visitINDEX(mii, node):
                assert len(node.children()) == 1
                myterm = node.children()[0]
                return node.__class__(myterm.__class__(self._fieldRename(myterm.children()[0])))
        return CqlIndexChangeVisitor(cqlAst).visit()


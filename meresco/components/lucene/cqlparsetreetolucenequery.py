## begin license ##
#
#    CQLParser is parser that builts up a parsetree for the given CQL and
#    can convert this into other formats.
#    Copyright (C) 2005-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of CQLParser
#
#    CQLParser is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    CQLParser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with CQLParser; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
from PyLucene import TermQuery, Term, BooleanQuery, BooleanClause, PhraseQuery

from cqlparser.cqlparser import parseString, CQL_QUERY, SCOPED_CLAUSE, SEARCH_CLAUSE, BOOLEAN, SEARCH_TERM, INDEX, RELATION, COMPARITOR, MODIFIER, UnsupportedCQL, CQLParseException

class ParseException(Exception):
    pass

def _termOrPhraseQuery(index, termString):
    listOfTermStrings = [termString.lower()]
    if ' ' in termString:
        listOfTermStrings = [x.lower() for x in termString.split(" ") if x]
    if len(listOfTermStrings) == 1:
        return TermQuery(Term(index, listOfTermStrings[0]))
    result = PhraseQuery()
    for term in listOfTermStrings:
        result.add(Term(index, term))
    return result

class CqlVisitor(object):
    def __init__(self, root):
        self._root = root

    def visit(self):
        return self._root.accept(self)

    def visitCQL_QUERY(self, node):
        if node.__class__ == CQL_QUERY:
            assert len(node.children()) == 1
            return node.children()[0].accept(self)

    def visitSCOPED_CLAUSE(self, node):
        if len(node.children()) == 1:
            return node.children()[0].accept(self)
        if len(node.children()) == 3:
            lhs = node.children()[0].accept(self)
            operator = node.children()[1].accept(self)
            rhs = node.children()[2].accept(self)
            lhsDict = {
                "AND": BooleanClause.Occur.MUST,
                "OR" : BooleanClause.Occur.SHOULD,
                "NOT": BooleanClause.Occur.MUST
            }
            rhsDict = lhsDict.copy()
            rhsDict["NOT"] = BooleanClause.Occur.MUST_NOT
            query = BooleanQuery()
            query.add(lhs, lhsDict[operator])
            query.add(rhs, rhsDict[operator])
            return query

    def visitINDEX(self, node):
        assert len(node.children()) == 1
        return node.children()[0]

    def visitRELATION(self, node):
        if len(node.children()) == 1:
            return node.children()[0].accept(self), '', ''
        assert len(node.children()) == 2
        relation = node.children()[0].accept(self)
        modifier, value = node.children()[1].accept(self)
        return relation, modifier, value

    def visitMODIFIER(self, node):
        assert len(node.children()) == 3
        name = node.children()[0]
        comparitor = node.children()[1]
        assert comparitor == "="
        value = node.children()[2]
        return name, value

    def visitCOMPARITOR(self, node):
        assert len(node.children()) == 1
        assert node.children()[0] in ['=', 'exact']
        return node.children()[0]

    def visitBOOLEAN(self, node):
        assert len(node.children()) == 1
        return node.children()[0].upper()

    def visitSEARCH_TERM(self, node):
        assert len(node.children()) == 1
        term = str(node.children()[0])
        if term[0] == '"':
            return term[1:-1] #.replace(r'\"', '"')
        return term

class CqlAst2LuceneVisitor(CqlVisitor):
    def __init__(self, unqualifiedTermFields, node):
        CqlVisitor.__init__(self, node)
        self._unqualifiedTermFields = unqualifiedTermFields

    def visitSEARCH_CLAUSE(self, node):
        if len(node.children()) == 1: #unqualified term
            unqualifiedRhs = node.children()[0].accept(self)
            if len(self._unqualifiedTermFields) == 1:
                fieldname, boost = self._unqualifiedTermFields[0]
                query = _termOrPhraseQuery(fieldname, unqualifiedRhs)
                query.setBoost(boost)
            else:
                query = BooleanQuery()
                for fieldname, boost in self._unqualifiedTermFields:
                    subQuery = _termOrPhraseQuery(fieldname, unqualifiedRhs)
                    subQuery.setBoost(boost)
                    query.add(subQuery, BooleanClause.Occur.SHOULD)
            return query
        if len(node.children()) == 3: #either ( ... ) or a=b
            if node.children()[0] == "(":
                return node.children()[1].accept(self)
            lhs = node.children()[0].accept(self)
            relation, modifier, value = node.children()[1].accept(self)
            rhs = node.children()[2].accept(self)
            if relation == 'exact':
                query = TermQuery(Term(lhs, rhs))
            else:
                query = _termOrPhraseQuery(lhs, rhs)
            if modifier:
                assert modifier == "boost"
                query.setBoost(float(value))
            return query

class Composer:
    def __init__(self, unqualifiedTermFields):
        self._unqualifiedTermFields = unqualifiedTermFields

    def compose(self, node):
        return CqlAst2LuceneVisitor(self._unqualifiedTermFields, node).visit()


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

class Composer(object):
    def __init__(self, unqualifiedTermFields):
        self._unqualifiedTermFields = unqualifiedTermFields

    def compose(self, node):
        if node.__class__ == CQL_QUERY:
            assert len(node.children()) == 1
            return self.compose(node.children()[0])
        if node.__class__ == SCOPED_CLAUSE:
            if len(node.children()) == 1:
                return self.compose(node.children()[0])
            if len(node.children()) == 3:
                lhs = self.compose(node.children()[0])
                operator = self.compose(node.children()[1])
                rhs = self.compose(node.children()[2])
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

        if node.__class__ in [INDEX]:
            assert len(node.children()) == 1
            return node.children()[0]
        if node.__class__ == SEARCH_CLAUSE:
            if len(node.children()) == 1: #unqualified term
                unqualifiedRhs = self.compose(node.children()[0])
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
                lhs = self.compose(node.children()[0])
                if lhs == "(":
                    return self.compose(node.children()[1])
                relation, modifier, value = self.compose(node.children()[1])
                rhs = self.compose(node.children()[2])
                if relation == 'exact':
                    query = TermQuery(Term(lhs, rhs))
                else:
                    query = _termOrPhraseQuery(lhs, rhs)
                if modifier:
                    assert modifier == "boost"
                    query.setBoost(float(value))
                return query
        if node.__class__ == RELATION:
            if len(node.children()) == 1:
                return self.compose(node.children()[0]), '', ''
            assert len(node.children()) == 2
            relation = self.compose(node.children()[0])
            modifier, value = self.compose(node.children()[1])
            return relation, modifier, value
        if node.__class__ == MODIFIER:
            assert len(node.children()) == 3
            name = self.compose(node.children()[0])
            comparitor = self.compose(node.children()[1])
            assert comparitor == "="
            value = self.compose(node.children()[2])
            return name, value
        if node.__class__ == COMPARITOR:
            assert len(node.children()) == 1
            assert node.children()[0] in ['=', 'exact']
            return node.children()[0]
        if node.__class__ == BOOLEAN:
            assert len(node.children()) == 1
            return node.children()[0].upper()
        if node.__class__ == SEARCH_TERM:
            assert len(node.children()) == 1
            term = self.compose(node.children()[0])
            if term[0] == '"':
                return term[1:-1] #.replace(r'\"', '"')
            return term
        if node.__class__ == str:
            return node
        raise Exception("Unknown token " + str(node))

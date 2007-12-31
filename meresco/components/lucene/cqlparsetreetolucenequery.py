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
from cqlparser import CqlVisitor

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

class CqlAst2LuceneVisitor(CqlVisitor):
    def __init__(self, unqualifiedTermFields, node):
        CqlVisitor.__init__(self, node)
        self._unqualifiedTermFields = unqualifiedTermFields

    def visitSCOPED_CLAUSE(self, node):
        clause = CqlVisitor.visitSCOPED_CLAUSE(self, node)
        if len(clause) == 1:
            return clause[0]
        lhs, operator, rhs = clause
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

    def visitSEARCH_CLAUSE(self, node):
        results = CqlVisitor.visitSEARCH_CLAUSE(self, node)
        if len(results) == 1:
            ((unqualifiedRhs,),) = results
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
        if len(results) == 3: #either "(" cqlQuery ")" or index relation searchTerm
            (((left,),), ((middle,),), (right,)) = results
            if left == "(":
                return middle
            if relation in ['==', 'exact']:
                self.query = TermQuery(Term(left, right))
            else:
                self.query = _termOrPhraseQuery(left, right)
            CqlVisitor.visitRELATION(self, middle)
            return self.query

    def visitRELATION(self, node):
        if len(node.children()) == 1:
            return
        if len(node.children()) == 3:
            relation, modifier, value = node.children()
            self.query.setBoost(float(value))

class Composer:
    def __init__(self, unqualifiedTermFields):
        self._unqualifiedTermFields = unqualifiedTermFields

    def compose(self, node):
        (result,) = CqlAst2LuceneVisitor(self._unqualifiedTermFields, node).visit()
        return result


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
#    along with $PROGRAM; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
from unittest import TestCase

from PyLucene import TermQuery, Term, BooleanQuery, BooleanClause, PhraseQuery

from cqlparser.cqlparser import parseString as parseCql
from meresco.components.lucene.cqlparsetreetolucenequery import Composer

class CqlParseTreeToLuceneQueryTest(TestCase):

    def testOneTermOutput(self):
        self.assertConversion(TermQuery(Term("unqualified", "cat")), "cat")

    def testRightHandSideIsLowercase(self):
        self.assertConversion(TermQuery(Term("unqualified", "cat")), "CaT")

    def testOneTermOutputWithANumber(self):
        self.assertConversion(TermQuery(Term("unqualified", "2005")), "2005")

    def testPhraseOutput(self):
        query = PhraseQuery()
        query.add(Term("unqualified", "cats"))
        query.add(Term("unqualified", "dogs"))
        self.assertConversion(query,'"cats dogs"')

    def testIndexRelationTermOutput(self):
        self.assertConversion(TermQuery(Term("animal", "cats")), 'animal=cats')
        query = PhraseQuery()
        query.add(Term("animal", "cats"))
        query.add(Term("animal", "dogs"))
        self.assertConversion(query, 'animal="cats dogs"')

    def testBooleanAndTermOutput(self):
        query = BooleanQuery()
        query.add(TermQuery(Term('unqualified', 'cats')), BooleanClause.Occur.MUST)
        query.add(TermQuery(Term('unqualified', 'dogs')), BooleanClause.Occur.MUST)
        self.assertConversion(query, 'cats AND dogs')

    def testBooleanOrTermOutput(self):
        query = BooleanQuery()
        query.add(TermQuery(Term('unqualified', 'cats')), BooleanClause.Occur.SHOULD)
        query.add(TermQuery(Term('unqualified', 'dogs')), BooleanClause.Occur.SHOULD)
        self.assertConversion(query, 'cats OR dogs')

    def testBooleanNotTermOutput(self):
        query = BooleanQuery()
        query.add(TermQuery(Term('unqualified', 'cats')), BooleanClause.Occur.MUST)
        query.add(TermQuery(Term('unqualified', 'dogs')), BooleanClause.Occur.MUST_NOT)
        self.assertConversion(query, 'cats NOT dogs')

    def testBraces(self):
        self.assertConversion(TermQuery(Term('unqualified', 'cats')), '(cats)')
        innerQuery = BooleanQuery()
        innerQuery.add(TermQuery(Term('unqualified', 'cats')), BooleanClause.Occur.MUST)
        innerQuery.add(TermQuery(Term('unqualified', 'dogs')), BooleanClause.Occur.MUST)
        outerQuery = BooleanQuery()
        outerQuery.add(innerQuery, BooleanClause.Occur.SHOULD)
        outerQuery.add(TermQuery(Term('unqualified', 'mice')), BooleanClause.Occur.SHOULD)

        self.assertConversion(outerQuery, '(cats AND dogs) OR mice')

    def testBoost(self):
        query = TermQuery(Term("title", "cats"))
        query.setBoost(2.0)
        self.assertConversion(query, "title =/boost=2.0 cats")

    def testUnqualifiedTermFields(self):
        result = Composer(unqualifiedTermFields=[("field0", 0.2), ("field1", 2.0)]).compose(parseCql("value"))

        query = BooleanQuery()
        left = TermQuery(Term("field0", "value"))
        left.setBoost(0.2)
        query.add(left, BooleanClause.Occur.SHOULD)

        right = TermQuery(Term("field1", "value"))
        right.setBoost(2.0)
        query.add(right, BooleanClause.Occur.SHOULD)

        self.assertEquals(query, result)

    def assertConversion(self, expected, input):
        result = Composer(unqualifiedTermFields=[("unqualified", 1.0)]).compose(parseCql(input))
        self.assertEquals(expected, result)


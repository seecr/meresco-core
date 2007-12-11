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

from PyLucene import TermQuery, Term, BooleanQuery, BooleanClause

from meresco.components.lucene.cqlparsetreetolucenequery import fromString as cqlToLucene, ParseException

class CqlParseTreeToLuceneQueryTest(TestCase):

    def testOneTermOutput(self):
        self.assertConversion(TermQuery(Term("__content__", "cat")), "cat")

    def testOneTermOutputWithANumber(self):
        self.assertConversion(TermQuery(Term("__content__", "2005")), "2005")

    def testPhraseOutput(self):
        self.assertConversion(TermQuery(Term("__content__", "cats dogs")),'"cats dogs"')

    def testIndexRelationTermOutput(self):
        self.assertConversion(TermQuery(Term("animal", "cats")), 'animal=cats')
        self.assertConversion(TermQuery(Term("animal", "cats dogs")), 'animal="cats dogs"')

    def testBooleanAndTermOutput(self):
        query = BooleanQuery()
        query.add(TermQuery(Term('__content__', 'cats')), BooleanClause.Occur.MUST)
        query.add(TermQuery(Term('__content__', 'dogs')), BooleanClause.Occur.MUST)
        self.assertConversion(query, 'cats AND dogs')

    def testBooleanOrTermOutput(self):
        query = BooleanQuery()
        query.add(TermQuery(Term('__content__', 'cats')), BooleanClause.Occur.SHOULD)
        query.add(TermQuery(Term('__content__', 'dogs')), BooleanClause.Occur.SHOULD)
        self.assertConversion(query, 'cats OR dogs')

    def testBooleanNotTermOutput(self):
        query = BooleanQuery()
        query.add(TermQuery(Term('__content__', 'cats')), BooleanClause.Occur.MUST)
        query.add(TermQuery(Term('__content__', 'dogs')), BooleanClause.Occur.MUST_NOT)
        self.assertConversion(query, 'cats NOT dogs')

    def testBraces(self):
        self.assertConversion(TermQuery(Term('__content__', 'cats')), '(cats)')
        innerQuery = BooleanQuery()
        innerQuery.add(TermQuery(Term('__content__', 'cats')), BooleanClause.Occur.MUST)
        innerQuery.add(TermQuery(Term('__content__', 'dogs')), BooleanClause.Occur.MUST)
        outerQuery = BooleanQuery()
        outerQuery.add(innerQuery, BooleanClause.Occur.SHOULD)
        outerQuery.add(TermQuery(Term('__content__', 'mice')), BooleanClause.Occur.SHOULD)

        self.assertConversion(outerQuery, '(cats AND dogs) OR mice')

    def xtestBoost(self):
        pass


    def assertConversion(self, expected, input):
        result = cqlToLucene(input)
        self.assertEquals(expected, result)

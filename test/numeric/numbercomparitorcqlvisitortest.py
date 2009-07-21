## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2009 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#
#    This file is part of Meresco Core.
#
#    Meresco Core is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Meresco Core is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Meresco Core; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from unittest import TestCase
from merescocore.components.numeric.numbercomparitorcqlvisitor import NumberComparitorCqlVisitor
from cqlparser import parseString

class NumberComparitorCqlVisitorTest(TestCase):

    def testGTE(self):
        ast = parseString('rating >= 23')
        expected = parseString('(rating.gte exact 3z OR (rating.gte exact 2z AND rating.gte exact z3))')

        self.assertEquals(expected, NumberComparitorCqlVisitor(ast, 'rating', convert=int, valueLength=2).visit())

    def testOnlyActOnGivenField(self):
        ast = parseString('someField >= 23')
        expected = parseString('someField >= 23')
        self.assertEquals(expected, NumberComparitorCqlVisitor(ast, 'rating', convert=int, valueLength=2).visit())

    def testNested(self):
        ast = parseString('field = value AND rating >= 2.3')
        expected = parseString('field = value AND (rating.gte exact 3z OR (rating.gte exact 2z AND rating.gte exact z3))')

        self.assertEquals(expected, NumberComparitorCqlVisitor(ast, 'rating', convert=lambda x: int(x.replace('.','')), valueLength=2).visit())

    def testVerySmallFigures(self):
        ast = parseString('rating < 2')
        expected = parseString('(rating.lte exact 0z AND rating.lte exact z1)')

        self.assertEquals(expected, NumberComparitorCqlVisitor(ast, 'rating', convert=int, valueLength=2).visit())
        expected = parseString('(rating.lte exact 0zzz AND (rating.lte exact z0zz AND (rating.lte exact zz0z AND rating.lte exact zzz1)))')
        self.assertEquals(expected, NumberComparitorCqlVisitor(ast, 'rating', convert=int, valueLength=4).visit())

    def testVeryLargeFigures(self):
        ast = parseString('rating > 97')
        expected = parseString('(rating.gte exact 9z AND rating.gte exact z8)')
        self.assertEquals(expected, NumberComparitorCqlVisitor(ast, 'rating', convert=int, valueLength=2).visit())

    def testLessThanZero(self):
        ast = parseString('rating < 0')
        expected = parseString('rating.lte exact zz')
        self.assertEquals(expected, NumberComparitorCqlVisitor(ast, 'rating', convert=int, valueLength=2).visit())

        ast = parseString('rating <= -10')
        self.assertEquals(expected, NumberComparitorCqlVisitor(ast, 'rating', convert=int, valueLength=2).visit())

    def testGreatThanMax(self):
        ast = parseString('rating > 99')
        expected = parseString('rating.gte exact zz')
        self.assertEquals(expected, NumberComparitorCqlVisitor(ast, 'rating', convert=int, valueLength=2).visit())

        ast = parseString('rating >= 2399')
        self.assertEquals(expected, NumberComparitorCqlVisitor(ast, 'rating', convert=int, valueLength=2).visit())
        
        

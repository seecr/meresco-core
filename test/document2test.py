## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school.
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

import unittest
from cq2utils import CallTrace
from meresco.components.lucene.document2 import IDFIELD, Document2, DocumentException

class Document2Test(unittest.TestCase):

    def testEmptyDocument2Fails(self):
        d = Document2('1')
        self.assertEquals(d.fields(), [IDFIELD])
        try:
            d.validate()
            self.fail()
        except DocumentException,e:
            self.assertEquals("Empty document", str(e))

    def testEmptyIdFails(self):
        try:
            d = Document2(' ')
            self.fail()
        except DocumentException,e:
            self.assertEquals('Empty ID', str(e))

    def testIdMustBeString(self):
        try:
            d = Document2(1234)
            self.fail()
        except DocumentException,e:
            self.assertEquals('Empty ID', str(e))

    def testAddInvalidField(self):
        d = Document2('1234')
        try:
            d.addIndexedField(None, None)
            self.fail()
        except DocumentException,e:
            self.assertEquals('Invalid fieldname: "None"', str(e))
        self.assertEquals(d.fields(), [IDFIELD])

    def testIgnoreEmptyField(self):
        d = Document2('1234')
        d.addIndexedField("x", None)
        self.assertEquals(d.fields(), [IDFIELD])

    def testAddField(self):
        d = Document2('1234')
        d.addIndexedField('x', 'a')
        d.addIndexedField('y', 'b')
        self.assertEquals(d.fields(), [IDFIELD, 'x', 'y'])
        d.validate()

    def testReservedFieldName(self):
        d = Document2('1234')
        try:
            d.addIndexedField(IDFIELD, 'not allowed')
            self.fail()
        except DocumentException,e:
            self.assertEquals('Invalid fieldname: "%s"' % IDFIELD, str(e))

    def testAddSameFieldTwice(self):
        d = Document2('1234')
        d.addIndexedField('x', 'a')
        d.addIndexedField('x', 'b')
        d.addToIndexWith(CallTrace("IndexWriter"))
        self.assertEquals([IDFIELD, 'x', 'x'], d.fields())

## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) SURF Foundation. http://www.surf.nl
#    Copyright (C) Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) SURFnet. http://www.surfnet.nl
#    Copyright (C) Stichting Kennisnet Ict op school. 
#       http://www.kennisnetictopschool.nl
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
import meresco.components.lucene.document
from meresco.components.lucene.document import IDFIELD, CONTENTFIELD, Document, DocumentException

class DocumentTest(unittest.TestCase):

	def setUp(self):
		self._contentField = False

	def testCreation(self):
		d = Document('1')
		self.assertEquals(d.fields(), [IDFIELD])
		
		try:
			d.validate()
			self.fail()
		except DocumentException,e:
			self.assertEquals("Empty document", str(e))

		try:
			d = Document(' ')
			self.fail()
		except DocumentException,e:
			self.assertEquals('Empty ID', str(e))

		try:
			d = Document(1234)
			self.fail()
		except DocumentException,e:
			self.assertEquals('Empty ID', str(e))

	def testAddInvalidField(self):
		d = Document('1234')
		try:
			d.addIndexedField(None, None)
			self.fail()
		except DocumentException,e:
			self.assertEquals('Invalid fieldname', str(e))
		self.assertEquals(d.fields(), [IDFIELD])
		
	def testIgnoreEmptyField(self):
		d = Document('1234')
		d.addIndexedField("x", None)
		self.assertEquals(d.fields(), [IDFIELD])

	def testAddField(self):
		d = Document('1234')
		d.addIndexedField('x', 'y')
		d.addIndexedField('y', 'x')
		self.assertEquals(d.fields(), [IDFIELD, 'x', 'y'])
		
		try:
			d.validate()
		except DocumentException,e:
			self.fail()
		
	def testContentField(self):
		d = Document('1234')
		d.addIndexedField('x', 'a')
		d.addIndexedField('y', 'b')
		self.assertEquals('a b', d.contentField())
		
	def testContentFieldDoesNotContainHiddenFields(self):
		d = Document('1234')
		d.addIndexedField('x', 'a')
		d.addIndexedField('__hidden__stuff', 'should remain hidden')
		d.addIndexedField('y', 'b')
		self.assertEquals('a b', d.contentField())
		
		
	def testAddToIndex(self):
		d = Document('1234')
		d.addIndexedField('x', 'y')
		d.addIndexedField('y', 'x')
		d.addToIndexWith(self)
		
		self.assertEquals(self._contentField, 'y x')

	def testReservedFieldName(self):
		d = Document('1234')
		try:
			d.addIndexedField(CONTENTFIELD, 'not allowed')
			self.fail()
		except DocumentException,e:
			self.assertEquals('Invalid fieldname', str(e))

		try:
			d.addIndexedField(IDFIELD, 'not allowed')
			self.fail()
		except DocumentException,e:
			self.assertEquals('Invalid fieldname', str(e))


	""" self-shunt """
	def addDocument(self, aDocument):
		self._contentField = aDocument.getField(CONTENTFIELD).stringValue()

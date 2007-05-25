## begin license ##
#
#    Teddy is the name for Seek You Too's Search Appliance.
#    Copyright (C) 2006 Stichting SURF. http://www.surf.nl
#    Copyright (C) 2006-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of Teddy.
#
#    Teddy is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Teddy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Teddy; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

import unittest
import document
from document import IDFIELD, CONTENTFIELD

class DocumentTest(unittest.TestCase):

	def setUp(self):
		self._contentField = False

	def testCreation(self):
		d = document.Document('1')
		self.assertEquals(d.fields(), [IDFIELD])
		
		try:
			d.validate()
			self.fail()
		except document.DocumentException,e:
			self.assertEquals("Empty document", str(e))

		try:
			d = document.Document(' ')
			self.fail()
		except document.DocumentException,e:
			self.assertEquals('Empty ID', str(e))

		try:
			d = document.Document(1234)
			self.fail()
		except document.DocumentException,e:
			self.assertEquals('Empty ID', str(e))

	def testAddInvalidField(self):
		d = document.Document('1234')
		try:
			d.addIndexedField(None, None)
			self.fail()
		except document.DocumentException,e:
			self.assertEquals('Invalid fieldname', str(e))
		self.assertEquals(d.fields(), [IDFIELD])
		
	def testIgnoreEmptyField(self):
		d = document.Document('1234')
		d.addIndexedField("x", None)
		self.assertEquals(d.fields(), [IDFIELD])

	def testAddField(self):
		d = document.Document('1234')
		d.addIndexedField('x', 'y')
		d.addIndexedField('y', 'x')
		self.assertEquals(d.fields(), [IDFIELD, 'x', 'y'])
		
		try:
			d.validate()
		except document.DocumentException,e:
			self.fail()
		
	def testContentField(self):
		d = document.Document('1234')
		d.addIndexedField('x', 'y')
		d.addIndexedField('y', 'x')
		self.assertEquals('y x', d.contentField())
		
	def testAddToIndex(self):
		d = document.Document('1234')
		d.addIndexedField('x', 'y')
		d.addIndexedField('y', 'x')
		d.addToIndexWith(self)
		
		self.assertEquals(self._contentField, 'y x')

	def testReservedFieldName(self):
		d = document.Document('1234')
		try:
			d.addIndexedField(document.CONTENTFIELD, 'not allowed')
			self.fail()
		except document.DocumentException,e:
			self.assertEquals('Invalid fieldname', str(e))

		try:
			d.addIndexedField(document.IDFIELD, 'not allowed')
			self.fail()
		except document.DocumentException,e:
			self.assertEquals('Invalid fieldname', str(e))


	""" self-shunt """
	def addDocument(self, aDocument):
		self._contentField = aDocument.getField(document.CONTENTFIELD).stringValue()

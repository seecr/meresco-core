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
#
# Document
#


import PyLucene

CONTENTFIELD = '__content__'
IDFIELD = '__id__'

class DocumentException(Exception):
	"""Generic Document Exception"""
	pass

class Document:
	
	def __init__(self, anId):
		if not self._isValidFieldValue(anId):
			raise DocumentException('Empty ID')
		
		self._document = PyLucene.Document()
		self._document.add(PyLucene.Field(IDFIELD, anId, PyLucene.Field.Store.YES, PyLucene.Field.Index.UN_TOKENIZED))
		self._fields = [IDFIELD]
		self._contentField = []
		
	def _isValidFieldValue(self, anObject):
		return type(anObject) == str and anObject.strip()
			
	def fields(self):
		return self._fields
	
	def _validFieldName(self, aKey):
		return self._isValidFieldValue(aKey) 	and \
			aKey.lower() not in [CONTENTFIELD, IDFIELD]

	def addIndexedField(self, aKey, aValue, tokenize = True):
		if not self._validFieldName(aKey):
				raise DocumentException('Invalid fieldname')
		
		if not self._isValidFieldValue(aValue):
			return
			
		self._addIndexedField(aKey, aValue, tokenize)
		self._fields.append(aKey)
		self._contentField.append(aValue)
		
	def _addIndexedField(self, aKey, aValue, tokenize = True):
		self._document.add(PyLucene.Field(aKey, aValue, PyLucene.Field.Store.NO, tokenize and PyLucene.Field.Index.TOKENIZED or PyLucene.Field.Index.UN_TOKENIZED))

		
	def contentField(self):
		return ' '.join(self._contentField)
	
	def addToIndexWith(self, anIndexWriter):
		self._addIndexedField(CONTENTFIELD, self.contentField())
		anIndexWriter.addDocument(self._document)
		
	def validate(self):
		if self._fields == [IDFIELD]:
			raise DocumentException('Empty document')

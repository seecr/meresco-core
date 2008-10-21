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

import PyLucene

IDFIELD = '__id__'

class DocumentException(Exception):
    """Generic Document Exception"""
    pass

class Document(object):

    def __init__(self, anId):
        self.identifier = anId
        if not self._isValidFieldValue(anId):
            raise DocumentException("Invalid ID: '%s'" % anId)
        self._document = PyLucene.Document()
        self._document.add(PyLucene.Field(IDFIELD, anId, PyLucene.Field.Store.YES, PyLucene.Field.Index.UN_TOKENIZED))
        self._fields = [IDFIELD]
        self.pokedDict = []

    def _isValidFieldValue(self, anObject):
        return isinstance(anObject, basestring) and anObject.strip()

    def fields(self):
        return self._fields

    def _validFieldName(self, aKey):
        return self._isValidFieldValue(aKey) and aKey.lower() != IDFIELD

    def addIndexedField(self, aKey, aValue, tokenize = True):
        if not self._validFieldName(aKey):
                raise DocumentException('Invalid fieldname: "%s"' % aKey)

        if not self._isValidFieldValue(aValue):
            return

        self._addIndexedField(aKey, aValue, tokenize)
        self._fields.append(aKey)

    def _addIndexedField(self, aKey, aValue, tokenize = True):
        self._document.add(PyLucene.Field(aKey, aValue, PyLucene.Field.Store.NO, tokenize and PyLucene.Field.Index.TOKENIZED or PyLucene.Field.Index.UN_TOKENIZED))

    def addToIndexWith(self, anIndexWriter):
        anIndexWriter.addDocument(self._document)

    def validate(self):
        if self._fields == [IDFIELD]:
            raise DocumentException('Empty document')

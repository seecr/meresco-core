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

class DocumentDict(object):
    def __init__(self):
        self._dict = {}

    def add(self, key, value):
        self.addField(DocumentField(key, value))

    def addField(self, documentField):
        fields = self.get(documentField.key)
        fields.append(documentField)
        self._dict[documentField.key] = fields

    def get(self, key):
        return self._dict.get(key, [])

    def __iter__(self):
        for fields in self._dict.itervalues():
            for documentField in fields:
                yield documentField

class DocumentField(object):

    def __init__(self, key, value, **kwargs):
        self.key = key
        self.value = value
        self.options = kwargs

    def __eq__(self, other):
        return type(other) == DocumentField and \
            self.key == other.key and \
            self.value == other.value and \
            self.options == other.options
            
    def __hash__(self):
        return hash(self.key)

    def __repr__(self):
        return '(%s => %s)' % (repr(self.key), repr(self.value))

def asDict(documentDict):
    result = {}
    for documentField in documentDict:
        value = result.get(documentField.key, [])
        value.append(documentField.value)
        result[documentField.key] = value
    return result

def fromDict(aDictionary):
    result = DocumentDict()
    for key,valueList in aDictionary.items():
        for value in valueList:
            result.add(key,value)
    return result

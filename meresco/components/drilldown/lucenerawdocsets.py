## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) 2007 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2007 Stichting Kennisnet Ict op school.
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
import PyLucene

class LuceneRawDocSets(object):
    def __init__(self, aLuceneIndexReader, fieldNames):
        self._reader = aLuceneIndexReader
        self._fieldNames = fieldNames

    def getDocSets(self):
        for fieldName in self._fieldNames:
            yield (fieldName, luceneRawDocSetsForField(self._reader, fieldName))

    def docCount(self):
        return self._reader.numDocs()

def luceneRawDocSetsForField(reader, fieldName):
    termDocs = reader.termDocs()
    termEnum = reader.terms(PyLucene.Term(fieldName, ''))
    #IndexReader.terms returns something of the following form, if fieldname == fieldname3
    #fieldname3 'abla'
    #fieldname3 'bb'
    #fielname3 'zz'
    #fieldname4 'aa'

    #The enum has the following (weird) behaviour: the internal pointer references
    #the first element by default, but when there are no elements it references a
    #None element. Therefor we have to check "if not term".
    #We use a "do ... while" idiom because calling next would advance the internal
    #pointer, resulting in a missed first element

    while True:
        term = termEnum.term()
        if not term or term.field() != fieldName:
            break
        termDocs.seek(term)

        yield (term.text(), _generateDocIds(termDocs))
        if not termEnum.next():
            break

def _generateDocIds(termDocs):
    result = []
    while termDocs.next():
        result.append(termDocs.doc())
    return result
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
from PyLucene import Term

class LuceneRawDocSets(object):
    """IndexReader.terms returns something of the following form, if fieldname == fieldname3
    fieldname3 'abla'
    fieldname3 'bb'
    fielname3 'zz'
    fieldname4 'aa'

    The enum has the following (weird) behaviour: the internal pointer references
    the first element by default, but when there are no elements it references a
    None element. Therefor we have to check "if not term".
    We use a "do ... while" idiom because calling next would advance the internal
    pointer, resulting in a missed first element
    """
    def __init__(self, aLuceneIndexReader, fieldNames):
        self._reader = aLuceneIndexReader
        self._fieldNames = fieldNames

    def getDocSets(self):
        termDocs = self._reader.termDocs()
        for field in sorted(self._fieldNames):
            yield (field, self._luceneRawDocSetsForField(field, termDocs))

    def _luceneRawDocSetsForField(self, field, termDocs):
        termEnum = self._reader.terms(Term(field, ''))
        while True:
            term = termEnum.term()
            if not term or term.field() != field:
                break;
            freq = termEnum.docFreq()
            termDocs.seek(termEnum)
            docIds, na = termDocs.read(freq)
            while len(docIds) != freq:
                docIdsBatch, na  = termDocs.read(freq - len(docIds))
                if docIdsBatch == []:
                    break
                docIds.extend(docIdsBatch)
            if len(docIds) > 0:
                yield (term.text(), docIds)
            if not termEnum.next():
                break

    def docCount(self):
        return self._reader.numDocs()

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
from meresco.framework import Observable
from meresco.components.lucene import Document

class Fields2LuceneDocument(Observable):

    def __init__(self, untokenized=[]):
        Observable.__init__(self)
        self._untokenized = untokenized
        self.txs = {}

    def begin(self):
        self.txs[self.tx.getId()] = Fields2LuceneDocumentTx(self, self._untokenized)

    def addField(self, name, value):
        self.txs[self.tx.getId()].addField(name, value)

    def commit(self):
        self.txs[self.tx.getId()].finalize()
        del self.txs[self.tx.getId()]


class Fields2LuceneDocumentTx(object):

    def __init__(self, parent, untokenized):
        self.parent = parent
        self.fields = {}
        self._untokenized = untokenized

    def addField(self, name, value):
        if not name in self.fields:
            self.fields[name] = []
        self.fields[name].append(value)

    def finalize(self):
        document = Document(self.fields['__id__'][0])
        del self.fields['__id__']
        for name, values in self.fields.items():
            for value in values:
                document.addIndexedField(name, value, not name in self._untokenized)
        self.parent.do.addDocument(document)



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

from StringIO import StringIO
from cq2utils.component import Component
from amara.binderytools import bind_string
from PyLucene import BooleanQuery, BooleanClause, ConstantScoreRangeQuery, Term, TermQuery, MatchAllDocsQuery
from meresco.components.lucene import Document
from cq2utils.uniquenumbergenerator import UniqueNumberGenerator


class OaiJazzLucene(Component):
    def __init__(self, anIndex, aStorage, aNumberGenerator = None):
        self._index = anIndex
        self._storage = aStorage
        self._numberGenerator = aNumberGenerator

    def add(self, id, name, *nodes):
        uniqueNumber = self._numberGenerator.next()
        document = Document(id)
        document.addIndexedField('__parts__.part', name, False)
        document.addIndexedField('__stamp__.unique', '%019i' % uniqueNumber, False)
        for node in nodes:
            if node.namespaceURI == "http://www.openarchives.org/OAI/2.0/":
                for s in node.setSpec:
                    document.addIndexedField('__set_membership__.set', str(s), False)
                self._storage.add(id, '__set_membership__', '<__set_membership__>%s</__set_membership__>' % (''.join('<setSpec>%s</setSpec>' % setSpec for setSpec in node.setSpec)))

        self._index.deleteID(id)
        self._index.addToIndex(document)

    def delete(self, id):
        #create thumbstone
        self._index.deleteID(id)

    def oaiSelect(self, oaiSet, prefix, continueAt, oaiFrom, oaiUntil):
        def addRange(root, field, lo, hi, inclusive):
            range = ConstantScoreRangeQuery(field, lo, hi, inclusive, inclusive)
            root.add(range, BooleanClause.Occur.MUST)

        #It is necessery here to work with the elemental objects, because the query parser transforms everything into lowercase
        query = BooleanQuery()
        query.add(TermQuery(Term('__parts__.part', prefix)), BooleanClause.Occur.MUST)

        if continueAt != '0':
            addRange(query, '__stamp__.unique', continueAt, None, False)
        if oaiFrom or oaiUntil:
            oaiFrom = oaiFrom or None
            oaiUntil = oaiUntil or None
            addRange(query, '__stamp__.datestamp', oaiFrom, oaiUntil, True)
        if oaiSet:
            query.add(TermQuery(Term('%s.%s' % ('__set_membership__', 'set'), oaiSet)), BooleanClause.Occur.MUST)

        return self._index.executeQuery(query, '__stamp__.unique')

    def listAll(self):
        return self._index.executeQuery(MatchAllDocsQuery())

    def getUnique(self, id):
        buffer = StringIO()
        self._storage.write(buffer, id, '__stamp__')
        return bind_string(buffer.getvalue()).__stamp__.unique

    def getDatestamp(self, id):
        buffer = StringIO()
        self._storage.write(buffer, id, '__stamp__')
        return bind_string(buffer.getvalue()).__stamp__.datestamp

    def getSets(self, id):
        buffer = StringIO()
        self._storage.write(buffer, id, '__set_membership__')
        return map(str, bind_string(buffer.getvalue()).__set_membership__.setSpec)

    def getParts(self, id):
        buffer = StringIO()
        self._storage.write(buffer, id, '__parts__')
        return map(str, bind_string(buffer.getvalue()).__parts__.part)

    def isDeleted(self, id):
        ignored, hasTombStone = self._storage.isAvailable(id, '__tombstone__')
        return hasTombStone




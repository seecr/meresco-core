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
from cq2utils.uniquenumbergenerator import UniqueNumberGenerator

from amara.binderytools import bind_string, bind_stream

from PyLucene import BooleanQuery, BooleanClause, ConstantScoreRangeQuery, Term, TermQuery, MatchAllDocsQuery

from meresco.framework import Observable
from meresco.components import Xml2Document, XmlParseAmara
from meresco.components.lucene import IndexComponent

def createOaiMeta(sets, prefixes, stamp, unique):
    yield '<oaimeta>'
    yield   '<sets>'
    for set in sets:
        yield '<setSpec>%s</setSpec>' % set
    yield   '</sets>'
    yield   '<prefixes>'
    for prefix in prefixes:
        yield '<prefix>%s</prefix>' % prefix
    yield   '</prefixes>'
    yield '<stamp>%s</stamp>' % stamp
    yield '<unique>%019i</unique>' % unique
    yield '</oaimeta>'

def parseOaiMeta(xmlStream):
    oaimeta = bind_stream(xmlStream).oaimeta

    setSpecList = oaimeta.sets.setSpec and oaimeta.sets.setSpec or []
    sets = set((str(setSpec) for setSpec in setSpecList))
    prefixList = oaimeta.prefixes.prefix and oaimeta.prefixes.prefix or []
    prefixes = set((str(prefix) for prefix in prefixList))
    stamp = str(oaimeta.stamp)
    unique = str(oaimeta.unique)
    return sets, prefixes, stamp, unique

class OaiJazzLucene(Observable):
    def __init__(self, anIndex, aStorage, aNumberGenerator = None):
        Observable.__init__(self)
        self.addObservers([(XmlParseAmara(), [(Xml2Document(), [IndexComponent(anIndex)])]), aStorage])
        self._numberGenerator = aNumberGenerator

    def add(self, id, name, *nodes):
        self.any.deletePart(id, 'tombstone')
        sets = set()
        prefixes = set()
        if (True, True) == self.any.isAvailable(id, 'oaimeta'):
            sets, prefixes, stamp, unique = parseOaiMeta(self.any.get(id, 'oaimeta'))
        prefixes.add(name)
        unique = self._numberGenerator.next()
        stamp = '?'
        for node in nodes:
            if node.namespaceURI == "http://www.openarchives.org/OAI/2.0/":
                sets.update(str(s) for s in node.setSpec)
        newOaiMeta = createOaiMeta(sets, prefixes, stamp, unique)
        self.do.add(id, 'oaimeta', ''.join(newOaiMeta))
        #self._index.add(id, 'oaimeta', bind_string(''.join(newOaiMeta)))

    def delete(self, id):
        self._storage.add(id, '__tombstone__', '<tombstone/>')

    def oaiSelect(self, oaiSet, prefix, continueAt, oaiFrom, oaiUntil):
        def addRange(root, field, lo, hi, inclusive):
            range = ConstantScoreRangeQuery(field, lo, hi, inclusive, inclusive)
            root.add(range, BooleanClause.Occur.MUST)

        #It is necessery here to work with the elemental objects, because the query parser transforms everything into lowercase
        query = BooleanQuery()
        query.add(TermQuery(Term('oaimeta.prefixes.prefix', prefix)), BooleanClause.Occur.MUST)

        if continueAt != '0':
            addRange(query, 'oaimeta.unique', continueAt, None, False)
        if oaiFrom or oaiUntil:
            oaiFrom = oaiFrom or None
            oaiUntil = oaiUntil or None
            addRange(query, 'oaimeta.datestamp', oaiFrom, oaiUntil, True)
        if oaiSet:
            query.add(TermQuery(Term('oaimeta.sets.setSpec', oaiSet)), BooleanClause.Occur.MUST)

        return self.any.executeQuery(query, 'oaimeta.unique')

    def listAll(self):
        return self.any.executeQuery(MatchAllDocsQuery())

    def getUnique(self, id):
        sets, prefixes, stamp, unique = parseOaiMeta(self.any.get(id, 'oaimeta'))
        return unique

    def getDatestamp(self, id):
        sets, prefixes, stamp, unique = parseOaiMeta(self._storage.get(id, 'oaimeta'))
        return stamp

    def getSets(self, id):
        sets, prefixes, stamp, unique = parseOaiMeta(self.any.get(id, 'oaimeta'))
        return list(sets)

    def getParts(self, id):
        sets, prefixes, stamp, unique = parseOaiMeta(self._storage.get(id, 'oaimeta'))
        buffer = StringIO()
        self.any.write(buffer, id, '__parts__')
        return map(str, bind_string(buffer.getvalue()).__parts__.part)

    def isDeleted(self, id):
        ignored, hasTombStone = self.any.isAvailable(id, '__tombstone__')
        return hasTombStone




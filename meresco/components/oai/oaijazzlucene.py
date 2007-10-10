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

from StringIO import StringIO
from time import strftime, gmtime, strptime, localtime, mktime
from re import compile

from cq2utils.uniquenumbergenerator import UniqueNumberGenerator
from cq2utils.xmlutils import findNamespaces

from amara.binderytools import bind_string, bind_stream

from PyLucene import BooleanQuery, BooleanClause, ConstantScoreRangeQuery, Term, TermQuery, MatchAllDocsQuery

from meresco.framework import Observable
from meresco.components import Xml2Document, XmlParseAmara
from meresco.components.lucene import IndexComponent

def createOaiMeta(sets, prefixes, stamp, unique):
    yield '<oaimeta xmlns:t="http://www.cq2.nl/teddy">'
    yield   '<sets>'
    for set in sets:
        yield '<setSpec t:tokenize="false">%s</setSpec>' % set
    yield   '</sets>'
    yield   '<prefixes>'
    for prefix in prefixes:
        yield '<prefix t:tokenize="false">%s</prefix>' % prefix
    yield   '</prefixes>'
    yield '<stamp t:tokenize="false">%s</stamp>' % stamp
    yield '<unique>%019i</unique>' % unique
    yield '</oaimeta>'

def parseOaiMeta(xmlString):
    oaimeta = bind_string(xmlString).oaimeta
    sets = set()
    if hasattr(oaimeta.sets, 'setSpec'):
        sets = set(str(setSpec) for setSpec in oaimeta.sets.setSpec)
    prefixes = set()
    if hasattr(oaimeta.prefixes, 'prefix_'):
        prefixes = set(str(prefix) for prefix in oaimeta.prefixes.prefix_)
    stamp = str(oaimeta.stamp)
    unique = str(oaimeta.unique)
    return sets, prefixes, stamp, unique

class OaiJazzLucene(Observable):
    def __init__(self, anIndex, aStorage, aNumberGenerator = None):
        Observable.__init__(self)
        self.addObservers([
            (XmlParseAmara(), [
                (Xml2Document(), [
                    IndexComponent(anIndex)])
                ]),
            aStorage])
        self._numberGenerator = aNumberGenerator
        def close():
            anIndex.close()
        self.close = close

    def _gettime(self):
        return gmtime()

    def updateOaiMeta(self, id, sets, prefixes):
        unique = self._numberGenerator.next()
        stamp =  strftime('%Y-%m-%dT%H:%M:%SZ', self._gettime())
        newOaiMeta = createOaiMeta(sets, prefixes, stamp, unique)
        metaRecord = ''.join(newOaiMeta)
        self.do.add(id, 'oaimeta', metaRecord)

    def getPreviousRecord(self, id):
        sets = set()
        prefixes = set()
        stamp = unique = None
        if (True, True) == self.any.isAvailable(id, 'oaimeta'):
            data = ''.join(self.any.getStream(id, 'oaimeta'))
            sets, prefixes, stamp, unique = parseOaiMeta(data)
        return sets, prefixes, stamp, unique

    def storeOaiInformation(self, *args, **kwargs):
        self.add(*args, **kwargs)


    def add(self, id, name, record, *nodes):
        self.any.deletePart(id, 'tombstone')
        sets, prefixes, na, na = self.getPreviousRecord(id)
        prefixes.add(name)
        self.updateAllPrefixes(name, record)
        for node in nodes:
            if node.localName == 'header' and node.namespaceURI == "http://www.openarchives.org/OAI/2.0/":
                sets.update(str(s) for s in node.setSpec)
                sets = self._flattenSetHierarchy(sets)
                self.updateAllSets(sets)
        self.updateOaiMeta(id, sets, prefixes)

    def delete(self, id):
        self.any.store(id, 'tombstone', '<tombstone/>')
        sets, prefixes, na, na = self.getPreviousRecord(id)
        self.updateOaiMeta(id, sets, prefixes)

    def oaiSelect(self, oaiSet, prefix, continueAt, oaiFrom, oaiUntil):
        def addRange(root, field, lo, hi, inclusive):
            range = ConstantScoreRangeQuery(field, lo, hi, inclusive, inclusive)
            root.add(range, BooleanClause.Occur.MUST)

        if self.any.numberOfDocuments() == 0:
            return []

        #It is necessery here to work with the elemental objects, because the query parser transforms everything into lowercase
        query = BooleanQuery()
        query.add(TermQuery(Term('oaimeta.prefixes.prefix', prefix)), BooleanClause.Occur.MUST)

        if continueAt != '0':
            addRange(query, 'oaimeta.unique', continueAt, None, False)
        if oaiFrom or oaiUntil:
            oaiFrom = oaiFrom or None
            oaiUntil = oaiUntil and self._fixUntilDate(oaiUntil) or None
            addRange(query, 'oaimeta.stamp', oaiFrom, oaiUntil, True)
        if oaiSet:
            query.add(TermQuery(Term('oaimeta.sets.setSpec', oaiSet)), BooleanClause.Occur.MUST)

        return self.any.executeQuery(query, 'oaimeta.unique')

    def listAll(self):
        return self.any.executeQuery(MatchAllDocsQuery())

    def _fixUntilDate(self, aString):
        dateRE = compile('^\d{4}-\d{2}-\d{2}$')
        result = aString
        if dateRE.match(aString):
            dateFromString = strptime(aString, '%Y-%m-%d')
            datePlusOneDay = localtime(mktime(dateFromString) + 24*3600)
            result = strftime('%Y-%m-%dT%H:%M:%SZ', datePlusOneDay)
        return result

    def _flattenSetHierarchy(self, sets):
        """"[1:2:3, 1:2:4] => [1, 1:2, 1:2:3, 1:2:4]"""
        result = set()
        for setSpec in sets:
            parts = setSpec.split(':')
            for i in range(1, len(parts) + 1):
                result.add(':'.join(parts[:i]))
        return result

    def getAllSets(self):
        allSets = set()
        if (True, True) == self.any.isAvailable('__all_sets__', '__sets__'):
            setsXml = bind_stream(self.any.getStream('__all_sets__', '__sets__'))
            allSets.update(str(setSpec) for setSpec in setsXml.__sets__.setSpec)
        return allSets

    def updateAllSets(self, sets):
        allSets = self.getAllSets()
        allSets.update(sets)
        spec= '<setSpec>%s</setSpec>'
        setsXml = '<__sets__>' + ''.join(spec % set for set in allSets) + '</__sets__>'
        self.any.store('__all_sets__', '__sets__', setsXml)

    def _getAllPrefixes(self):
        allPrefixes = {}
        if (True, True) == self.any.isAvailable('__all_prefixes__', '__prefixes__'):
            allPrefixesXml = bind_stream(self.any.getStream('__all_prefixes__', '__prefixes__')).ListMetadataFormats
            for info in allPrefixesXml.metadataFormat:
                allPrefixes[str(info.metadataPrefix)] = (str(info.schema), str(info.metadataNamespace))
        return allPrefixes

    def getAllPrefixes(self):
        return set((prefix, xsd, ns) for prefix, (xsd, ns) in self._getAllPrefixes().items())

    def findSchema(self, record):
        if 'amara.bindery.root_base' in str(type(record)):
            record = record.childNodes[0]
        ns2xsd = {}
        if hasattr(record, 'schemaLocation'):
            nsXsdList = record.schemaLocation.split()
            for n in range(0, len(nsXsdList), 2):
                ns2xsd[nsXsdList[n]] = nsXsdList[n+1]
        return ns2xsd

    def updateAllPrefixes(self, prefix, record):
        if 'amara.bindery.root_base' in str(type(record)):
            record = record.childNodes[0]
        allPrefixes = self._getAllPrefixes()
        ns2xsd = self.findSchema(record)
        nsmap = findNamespaces(record)
        ns = nsmap[record.prefix]
        newPrefixInfo = (ns2xsd.get(ns,''), ns)
        if prefix not in allPrefixes or newPrefixInfo > allPrefixes[prefix]:
            allPrefixes[prefix] = newPrefixInfo
        prefixTemplate = '<metadataFormat><metadataPrefix>%s</metadataPrefix><schema>%s</schema><metadataNamespace>%s</metadataNamespace></metadataFormat>'
        prefixesXml = '<ListMetadataFormats>' + ''.join(prefixTemplate % (prefix, xsd, ns) for prefix, (xsd, ns) in allPrefixes.items()) + '</ListMetadataFormats>'
        self.any.store('__all_prefixes__', '__prefixes__', prefixesXml)

    def getUnique(self, id):
        sets, prefixes, stamp, unique = self.getPreviousRecord(id)
        return unique

    def getDatestamp(self, id):
        sets, prefixes, stamp, unique = self.getPreviousRecord(id)
        return stamp

    def getSets(self, id):
        sets, prefixes, stamp, unique = self.getPreviousRecord(id)
        return list(sets)

    def getParts(self, id):
        sets, prefixes, stamp, unique = self.getPreviousRecord(id)
        return list(prefixes)

    def isDeleted(self, id):
        ignored, hasTombStone = self.any.isAvailable(id, 'tombstone')
        return hasTombStone

    def isAvailable(self, id):
        hasRecord, hasMeta = self.any.isAvailable(id, 'oaimeta')
        return hasRecord and hasMeta

    def listSets(self):
        return list(self.getAllSets())



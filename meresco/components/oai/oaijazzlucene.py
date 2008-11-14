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

from StringIO import StringIO
from time import strftime, gmtime, strptime, localtime, mktime
from re import compile

from cq2utils.xmlutils import findNamespaces

from amara.binderytools import bind_string, bind_stream
from lxml.etree import parse

from PyLucene import BooleanQuery, BooleanClause, ConstantScoreRangeQuery, Term, TermQuery, MatchAllDocsQuery

from meresco.framework import Observable, Transparant, be
from meresco.components import XmlParseAmara
from meresco.components.oai.xml2document import Xml2Document

def createOaiMeta(sets, prefixes, stamp, unique):
    yield '<oaimeta xmlns="http://meresco.com/namespace/meresco/oai/meta" xmlns:t="http://www.cq2.nl/teddy">'
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

prefixTemplate = '<metadataFormat><metadataPrefix>%s</metadataPrefix><schema>%s</schema><metadataNamespace>%s</metadataNamespace></metadataFormat>'

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
        be((self,
            (XmlParseAmara(),
                (Xml2Document(),
                    (anIndex,)
                )
            ),
            (aStorage, ),
            )
        )
        self._numberGenerator = aNumberGenerator
        def close():
            anIndex.close()
        self.close = close

    def addOaiRecord(self, identifier, sets=[], metadataFormats=[]):
        self.any.deletePart(identifier, 'tombstone')
        setSpecs, prefixes, na, na = self._getPreviousRecord(identifier)
        prefixes.update(prefix for prefix, schema, namespace in metadataFormats)
        assert prefixes, 'No metadataFormat specified for record with identifier "%s"' % identifier
        setSpecs.update(setSpec for setSpec, setName in sets)
        setSpecs = self._flattenSetHierarchy(setSpecs)
        self.__updateAllPrefixes2(metadataFormats)
        self._updateAllSets(setSpecs)
        self._updateOaiMeta(identifier, setSpecs, prefixes)


    def add(self, id, name, record):
        # This is the old way of adding data to OAI. Some self-learning stuff
        # is still applied, this should be refactored to special components
        # addOaiRecord will be the new way today.
        sets=set()
        if record.localName == "header" and record.namespaceURI == "http://www.openarchives.org/OAI/2.0/" and getattr(record, 'setSpec', None):
            sets.update((str(s), str(s)) for s in record.setSpec)

        if 'amara.bindery.root_base' in str(type(record)):
            record = record.childNodes[0]
        ns2xsd = self._findSchema(record)
        nsmap = findNamespaces(record)
        ns = nsmap[record.prefix]
        schema, namespace = (ns2xsd.get(ns,''), ns)
        metadataFormats=[(name, schema, namespace)]

        self.addOaiRecord(identifier=id, sets=sets, metadataFormats=metadataFormats)

    def delete(self, id):
        self.any.store(id, 'tombstone', '<tombstone/>')
        sets, prefixes, na, na = self._getPreviousRecord(id)
        self._updateOaiMeta(id, sets, prefixes)

    def oaiSelect(self, oaiSet=None, prefix='oai_dc', continueAt='0', oaiFrom=None, oaiUntil=None):
        def addRange(root, field, lo, hi, inclusive):
            range = ConstantScoreRangeQuery(field, lo, hi, inclusive, inclusive)
            root.add(range, BooleanClause.Occur.MUST)

        if self.any.docCount() == 0:
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

    def getAllPrefixes(self):
        return set((prefix, xsd, ns) for prefix, (xsd, ns) in self._getAllPrefixes().items())

    def getUnique(self, id):
        sets, prefixes, stamp, unique = self._getPreviousRecord(id)
        return unique

    def getDatestamp(self, id):
        sets, prefixes, stamp, unique = self._getPreviousRecord(id)
        return stamp

    def getSets(self, id):
        sets, prefixes, stamp, unique = self._getPreviousRecord(id)
        return list(sets)

    def getParts(self, id):
        sets, prefixes, stamp, unique = self._getPreviousRecord(id)
        return list(prefixes)

    def isDeleted(self, id):
        ignored, hasTombStone = self.any.isAvailable(id, 'tombstone')
        return hasTombStone

    def oaiRecordExists(self, id):
        hasRecord, hasMeta = self.any.isAvailable(id, 'oaimeta')
        return hasRecord and hasMeta

    def listSets(self):
        return list(self._getAllSets())

###############################################################################
    # test only?
    def listAll(self):
        return self.any.executeQuery(MatchAllDocsQuery())

###############################################################################

    def _findSchema(self, record):
        if 'amara.bindery.root_base' in str(type(record)):
            record = record.childNodes[0]
        ns2xsd = {}
        if hasattr(record, 'schemaLocation'):
            nsXsdList = record.schemaLocation.split()
            for n in range(0, len(nsXsdList), 2):
                ns2xsd[nsXsdList[n]] = nsXsdList[n+1]
        return ns2xsd

    def __updateAllPrefixes2(self, metadataFormats):
        allPrefixes = self._getAllPrefixes()
        for prefix, schema, namespace in metadataFormats:
            if prefix not in allPrefixes:
               allPrefixes[prefix] = (schema, namespace)
        prefixesXml = '<ListMetadataFormats>%s</ListMetadataFormats>' % \
            ''.join(prefixTemplate % (prefix, xsd, ns) \
                for prefix, (xsd, ns) in allPrefixes.items())
        self.any.store('__all_prefixes__', '__prefixes__', prefixesXml)

    def _updateAllPrefixes(self, prefix, record):
        if 'amara.bindery.root_base' in str(type(record)):
            record = record.childNodes[0]
        allPrefixes = self._getAllPrefixes()
        ns2xsd = self._findSchema(record)
        nsmap = findNamespaces(record)
        ns = nsmap[record.prefix]
        newPrefixInfo = (ns2xsd.get(ns,''), ns)
        if prefix not in allPrefixes:
            allPrefixes[prefix] = newPrefixInfo
        prefixesXml = '<ListMetadataFormats>' + ''.join(prefixTemplate % (prefix, xsd, ns) for prefix, (xsd, ns) in allPrefixes.items()) + '</ListMetadataFormats>'
        self.any.store('__all_prefixes__', '__prefixes__', prefixesXml)

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

    def _getAllSets(self):
        allSets = set()
        if (True, True) == self.any.isAvailable('__all_sets__', '__sets__'):
            setsXml = parse(self.any.getStream('__all_sets__', '__sets__'))
            allSets.update(setsXml.xpath('/sets:__sets__/sets:setSpec/text()', {'sets':'http://meresco.com/namespace/meresco/oai/sets'}))
        return allSets

    def _updateAllSets(self, sets):
        allSets = self._getAllSets()
        allSets.update(sets)
        spec= '<setSpec>%s</setSpec>'
        setsXml = '<__sets__ xmlns="http://meresco.com/namespace/meresco/oai/sets">' + ''.join(spec % set for set in allSets) + '</__sets__>'
        self.any.store('__all_sets__', '__sets__', setsXml)

    def _getAllPrefixes(self):
        allPrefixes = {}
        if (True, True) == self.any.isAvailable('__all_prefixes__', '__prefixes__'):
            allPrefixesXml = bind_stream(self.any.getStream('__all_prefixes__', '__prefixes__')).ListMetadataFormats
            for info in allPrefixesXml.metadataFormat:
                allPrefixes[str(info.metadataPrefix)] = (str(info.schema), str(info.metadataNamespace))
        return allPrefixes

    def _gettime(self):
        return gmtime()

    def _updateOaiMeta(self, id, sets, prefixes):
        unique = self._numberGenerator.next()
        stamp =  strftime('%Y-%m-%dT%H:%M:%SZ', self._gettime())
        newOaiMeta = createOaiMeta(sets, prefixes, stamp, unique)
        metaRecord = ''.join(newOaiMeta)
        self.do.add(id, 'oaimeta', str(metaRecord))

    def _getPreviousRecord(self, id):
        sets = set()
        prefixes = set()
        stamp = unique = None
        if (True, True) == self.any.isAvailable(id, 'oaimeta'):
            data = ''.join(self.any.getStream(id, 'oaimeta'))
            sets, prefixes, stamp, unique = parseOaiMeta(data)
        return sets, prefixes, stamp, unique

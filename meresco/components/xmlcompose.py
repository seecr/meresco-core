## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
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

from meresco.core import Observable
from lxml.etree import parse
from xml.sax.saxutils import escape as xmlEscape

class XmlCompose(Observable):
    def __init__(self, template, nsMap, **fieldMapping):
        Observable.__init__(self)
        self._template = template
        self._nsMap = nsMap
        self._fieldMapping = fieldMapping
    
    def getRecord(self, aRecordId):
        data = {}
        cachedRecord = {}
        for tagName, values in self._fieldMapping.items():
            partname, xPathExpression = values
            if not partname in cachedRecord:
                cachedRecord[partname] = self._getPart(aRecordId, partname)
            xml = cachedRecord[partname]
            result = xml.xpath(xPathExpression, namespaces=self._nsMap)
            if result:
                data[tagName] = str(result[0])
        yield self.createRecord(data)

    def createRecord(self, data):
        if len(data) != len(self._fieldMapping):
            raise StopIteration
        return self._template % dict(((k, xmlEscape(v)) for k,v in data.items()))

    def _getPart(self, recordId, partname):
        return parse(self.any.getStream(recordId, partname))

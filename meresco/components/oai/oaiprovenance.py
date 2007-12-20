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
from lxml.etree import parse

from meresco.framework import Observable


PROVENANCE_TEMPLATE = """<provenance xmlns="http://www.openarchives.org/OAI/2.0/provenance"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/provenance
                      http://www.openarchives.org/OAI/2.0/provenance.xsd">

<originDescription harvestDate="%(harvestDate)s" altered="true">
  <baseURL>%(baseURL)s</baseURL>
  <identifier>%(identifier)s</identifier>
  <datestamp>%(datestamp)s</datestamp>
  <metadataNamespace>%(metadataNamespace)s</metadataNamespace>
</originDescription>
</provenance>
"""

class OaiProvenance(Observable):

    def __init__(self, fieldMapping, nsMap={}):
        Observable.__init__(self)
        self._fieldMapping = fieldMapping
        self._nsMap = nsMap

    def provenance(self, aRecordId):
        provenanceData = {}
        cachedData = {}
        for tagName in self._fieldMapping:
            partname, xPathExpression = self._fieldMapping[tagName]
            if not partname in cachedData:
                cachedData[partname] = self._getPart(aRecordId, partname)

            xml = parse(StringIO(cachedData[partname]))

            result = xml.xpath(xPathExpression, self._nsMap)
            if result:
                provenanceData[tagName] = result[0].text

        provenanceResult = ''
        if len(provenanceData) != len(self._fieldMapping):
            raise StopIteration
        yield PROVENANCE_TEMPLATE % provenanceData

    def _getPart(self, recordId, partname):
        stream = StringIO()
        self.any.write(stream, recordId, partname)
        return stream.getvalue()

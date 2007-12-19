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
from xml.sax.saxutils import escape as xmlEscape
from amara.binderytools import bind_string
from StringIO import StringIO

from meresco.components.oai.oaiverb import OaiVerb

class OaiRecordVerb(OaiVerb):

    def writeRecord(self, webRequest, id, writeBody=True, showProvenance=False):
        isDeletedStr = self.any.isDeleted(id) and ' status="deleted"' or ''
        datestamp = self.any.getDatestamp(id)
        setSpecs = self._getSetSpecs(id)
        if writeBody:
            webRequest.write('<record>')

        webRequest.write("""<header %s>
            <identifier>%s</identifier>
            <datestamp>%s</datestamp>
            %s
        </header>""" % (isDeletedStr, xmlEscape(id.encode('utf-8')), datestamp, setSpecs))

        if writeBody and not isDeletedStr:
            webRequest.write('<metadata>')
            self.any.write(webRequest, id, self._metadataPrefix)
            webRequest.write('</metadata>')

        if showProvenance:
            meta = bind_string(self._getPartFromStorage(id, 'meta')).meta
            header = bind_string(self._getPartFromStorage(id, 'header')).header

            harvestdate = xmlEscape(str(meta.repository.harvestdate))
            baseURL = xmlEscape(str(meta.repository.baseurl))
            identifier = xmlEscape(str(header.identifier))
            datestamp = xmlEscape(str(header.datestamp))
            metadataNamespace = xmlEscape(str(meta.repository.metadataNamespace))
            webRequest.write("""<about>
<provenance xmlns="http://www.openarchives.org/OAI/2.0/provenance"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/provenance
                      http://www.openarchives.org/OAI/2.0/provenance.xsd">

<originDescription harvestDate="%(harvestdate)s" altered="true">
  <baseURL>%(baseURL)s</baseURL>
  <identifier>%(identifier)s</identifier>
  <datestamp>%(datestamp)s</datestamp>
  <metadataNamespace>%(metadataNamespace)s</metadataNamespace>
</originDescription>

</provenance>
</about>
""" % locals())
        if writeBody:
            webRequest.write('</record>')

    def _getSetSpecs(self, id):
        sets = self.any.getSets(id)
        if sets:
            return ''.join('<setSpec>%s</setSpec>' % xmlEscape(setSpec) for setSpec in sets)
        return ''

    def _getPartFromStorage(self, anId, aPartname):
        stream = StringIO()
        self.any.write(stream, anId, aPartname)
        return stream.getvalue()

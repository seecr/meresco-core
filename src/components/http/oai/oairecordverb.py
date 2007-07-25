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
from meresco.components.http.oai.oaitool import OaiVerb
from meresco.components.stampcomponent import DATESTAMP, STAMP_PART
from xml.sax.saxutils import escape as xmlEscape

class OaiRecordVerb(OaiVerb):
    
    def writeRecord(self, webRequest, id, writeBody = True):
        isDeletedStr = self._isDeleted(id) and ' status="deleted"' or ''
        datestamp = str(getattr(self.xmlSteal(id, STAMP_PART), DATESTAMP))
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
            self.do.write(webRequest, id, self._metadataPrefix)
            webRequest.write('</metadata>')
        if writeBody:
            webRequest.write('</record>')

    def _isDeleted(self, id):
        aTuple = self.any.isAvailable(id, "__tombstone__")
        ignored, hasTombstonePart = aTuple or (False, False)
        return hasTombstonePart
    
    def _getSetSpecs(self, id):
        aTuple = self.any.isAvailable(id, "__sets__")
        ignored, hasSetsPart = aTuple or (False, False)
        if hasSetsPart:
            sets = self.xmlSteal(id, "__sets__") 
            if hasattr(sets, 'set'):
                l = []
                for set in sets.set:
                    l.append(set.setSpec)
                return "".join(map(lambda setSpec: "<setSpec>%s</setSpec>" % setSpec, l))
        return ""

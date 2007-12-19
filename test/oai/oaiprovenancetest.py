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

from cq2utils.cq2testcase import CQ2TestCase
from cq2utils.calltrace import CallTrace

from meresco.framework import Observable
from meresco.components.oai.oaiprovenance import OaiProvenance

class OaiProvenanceTest(CQ2TestCase):

    def testProvenance(self):
        class MockStorage(object):
            def write(innerself, stream, ident, partname):
                if partname == 'meta':
                    stream.write("<meta><repository><metadataNamespace>METADATANAMESPACE</metadataNamespace><baseurl>BASEURL</baseurl><harvestDate>HARVESTDATE</harvestDate></repository></meta>")
                elif partname == 'header':
                    stream.write("<header><identifier>IDENTIFIER</identifier><datestamp>DATESTAMP</datestamp></header>")

        observable = Observable()
        provenance = OaiProvenance({
            'baseURL':('meta','meta/repository/baseurl'),
            'harvestDate': ('meta', 'meta/repository/harvestDate'),
            'metadataNamespace': ('meta', 'meta/repository/metadataNamespace'),
            'identifier': ('header', 'header/identifier'),
            'datestamp': ('header', 'header/datestamp'),
            })
        observable.addObserver(provenance)
        observer = MockStorage()
        provenance.addObserver(observer)

        result = ''.join(list(observable.any.provenance("recordId")))
        self.assertEqualsWS(result, """<provenance xmlns="http://www.openarchives.org/OAI/2.0/provenance"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/provenance
                      http://www.openarchives.org/OAI/2.0/provenance.xsd">

<originDescription harvestDate="HARVESTDATE" altered="true">
  <baseURL>BASEURL</baseURL>
  <identifier>IDENTIFIER</identifier>
  <datestamp>DATESTAMP</datestamp>
  <metadataNamespace>METADATANAMESPACE</metadataNamespace>
</originDescription>
</provenance>""")

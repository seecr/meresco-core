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

from oaitestcase import OaiTestCase

from meresco.components.oai import OaiIdentify

class OaiIdentifyTest(OaiTestCase):

    def getSubject(self):
        return OaiIdentify(repositoryName = 'Repository Name', adminEmail = 'admin@meresco.org')

    def testIdentify(self):
        self.request.args = {'verb': ['Identify']}

        self.observable.any.unknown('identify', self.request)

        self.assertEquals("setHeader('content-type', 'text/xml; charset=utf-8')",  str(self.request.calledMethods[0]))
        self.assertEqualsWS(self.OAIPMH % """
        <request verb="Identify">http://server:9000/path/to/oai</request>
<Identify>
    <repositoryName>Repository Name</repositoryName>
    <baseURL>http://server:9000/path/to/oai</baseURL>
    <protocolVersion>2.0</protocolVersion>
    <adminEmail>admin@meresco.org</adminEmail>
    <earliestDatestamp>1970-01-01T00:00:00Z</earliestDatestamp>
    <deletedRecord>persistent</deletedRecord>
    <granularity>YYYY-MM-DDThh:mm:ssZ</granularity>
  </Identify>""", self.stream.getvalue())
        self.assertValidString(self.stream.getvalue())

    def testIllegalArguments(self):
        self.assertBadArgument('identify', {'verb': ['Identify'], 'metadataPrefix': ['oai_dc']}, 'Argument(s) "metadataPrefix" is/are illegal.')

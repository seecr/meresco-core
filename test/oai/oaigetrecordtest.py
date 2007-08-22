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

from oaitestcase import OaiTestCase

from mockoaijazz import MockOaiJazz

from meresco.components.oai.oaigetrecord import OaiGetRecord
from meresco.components.oai.oaivalidator import assertValidString
from cq2utils.calltrace import CallTrace

class OaiGetRecordTest(OaiTestCase):
    def getSubject(self):
        return OaiGetRecord(['oai_dc'])

    def testGetRecordNoArguments(self):
        self.assertBadArgument('getRecord', {'verb': ['GetRecord']}, 'Missing argument(s) "identifier" and "metadataPrefix".')

    def testGetNoMetadataPrefix(self):
        self.assertBadArgument('getRecord', {'verb': ['GetRecord'], 'identifier': ['oai:ident']}, 'Missing argument(s) "metadataPrefix".')

    def testGetNoIdentifierArgument(self):
        self.assertBadArgument('getRecord', {'verb': ['GetRecord'], 'metadataPrefix': ['oai_dc']}, 'Missing argument(s) "identifier".')

    def testNonsenseArgument(self):
        self.assertBadArgument('getRecord', {'verb': ['GetRecord'], 'metadataPrefix': ['aPrefix'], 'identifier': ['anIdentifier'], 'nonsense': ['bla']}, 'Argument(s) "nonsense" is/are illegal.')

    def testDoubleArguments(self):
        self.assertBadArgument('getRecord', {'verb':['GetRecord'], 'metadataPrefix': ['oai_dc'], 'identifier': ['oai:ident', '2']}, 'Argument "identifier" may not be repeated.')

    def testGetRecordNotAvailable(self):
        self.request.args = {'verb':['GetRecord'], 'metadataPrefix': ['oai_dc'], 'identifier': ['oai:ident']}

        observer = CallTrace('RecordAnswering')
        notifications = []
        def isAvailable(id, partName):
            notifications.append((id, partName))
            return False, False
        observer.isAvailable = isAvailable
        observer.returnValues['getDatestamp'] = 'DATESTAMP_FOR_TEST'
        self.subject.addObserver(observer)

        self.observable.any.getRecord(self.request)

        self.assertEqualsWS(self.OAIPMH % """
<request identifier="oai:ident" metadataPrefix="oai_dc" verb="GetRecord">http://server:9000/path/to/oai</request>
<error code="idDoesNotExist">The value of the identifier argument is unknown or illegal in this repository.</error>""", self.stream.getvalue())
        assertValidString(self.stream.getvalue())

        self.assertEquals([('oai:ident', 'oai_dc')], notifications)

    def testGetRecord(self):
        self.request.args = {'verb':['GetRecord'], 'metadataPrefix': ['oai_dc'], 'identifier': ['oai:ident']}

        self.subject.addObserver(MockOaiJazz(
            isAvailableDefault=(True, False),
            isAvailableAnswer=[(None, 'oai_dc', (True,True))]))
        self.observable.any.getRecord(self.request)
        self.assertEqualsWS(self.OAIPMH % """
<request identifier="oai:ident"
 metadataPrefix="oai_dc"
 verb="GetRecord">http://server:9000/path/to/oai</request>
   <GetRecord>
   <record>
    <header>
      <identifier>oai:ident</identifier>
      <datestamp>DATESTAMP_FOR_TEST</datestamp>
    </header>
    <metadata>
      <some:recorddata xmlns:some="http://some.example.org" id="oai:ident"/>
    </metadata>
  </record>
 </GetRecord>""", self.stream.getvalue())

    def testDeletedRecord(self):
        self.request.args = {'verb':['GetRecord'], 'metadataPrefix': ['oai_dc'], 'identifier': ['oai:ident']}

        self.subject.addObserver(MockOaiJazz(
            isAvailableDefault=(True, False),
            isAvailableAnswer=[(None, "oai_dc", (True, True))],
            deleted=['oai:ident']))
        self.observable.any.getRecord(self.request)
        self.assertTrue("deleted" in self.stream.getvalue(), self.stream.getvalue())

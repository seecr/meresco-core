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

from os.path import join

from oaitestcase import OaiTestCase
from meresco.components.oai import OaiListSets, OaiJazzLucene
from meresco.components.lucene import LuceneIndex
from meresco.components import StorageComponent

class OaiListSetsTest(OaiTestCase):
    def getSubject(self):
        return OaiListSets()

    def testNonsenseArguments(self):
        self.assertBadArgument('listSets', {'verb': ['ListSets'], 'nonsense': ['aDate'], 'nonsense': ['more nonsense'], 'bla': ['b']}, 'Argument(s) "bla", "nonsense" is/are illegal.')

    def testListSetsNoArguments(self):
        jazz = OaiJazzLucene(LuceneIndex(join(self.tempdir,'index')),
            StorageComponent(join(self.tempdir,'storage')), iter(xrange(99)))
        self.request.args = {'verb':['ListSets']}
        self.subject.addObserver(jazz)
        self.subject.listSets(self.request)
        self.assertEqualsWS(self.OAIPMH % """
<request verb="ListSets">http://server:9000/path/to/oai</request>
 <ListSets>
   <set><setSpec>some:name:id_0</setSpec><setName>Some Name</setName></set>
   <set><setSpec>some:name:id_1</setSpec><setName>Some Name</setName></set>
 </ListSets>""", self.stream.getvalue())
        self.assertFalse('<resumptionToken' in self.stream.getvalue())

    def testResumptionTokensNotSupported(self):
        self.assertBadArgument('listSets', {'verb': ['ListSets'], 'resumptionToken': ['someResumptionToken']}, errorCode = "badResumptionToken")


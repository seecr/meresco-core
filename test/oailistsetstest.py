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
from meresco.queryserver.observers.oailistsets import OaiListSets

class OaiListSetsTest(OaiTestCase):
	def getSubject(self):
		return OaiListSets()
	
	def testNonsenseArguments(self):
		self.assertBadArgument({'verb': ['ListSets'], 'nonsense': ['aDate'], 'nonsense': ['more nonsense'], 'bla': ['b']}, 'Argument(s) "bla", "nonsense" is/are illegal.')

	def testListSetsNoArguments(self):
		self.request.args = {'verb':['ListSets']}
		
		class Observer:
			def listRecords(sself, partName, continueAt = '0', oaiFrom = None, oaiUntil = None, oaiSet=''):
				self.assertEquals('set', partName)
				self.assertEquals('0', continueAt)
				self.assertEquals(None, oaiFrom)
				self.assertEquals(None, oaiUntil)
				return ['id_0', 'id_1']
					
			def write(sself, sink, id, partName):
				if partName == 'set':
					sink.write('<set><setSpec>some:name:%s</setSpec><setName>Some Name</setName></set>' % id)
				else:
					self.fail(partName + ' is unexpected')
			
			def undo(sself, *args, **kwargs):
				pass
			def notify(sself, *args, **kwargs):
				pass
		
		self.subject.addObserver(Observer())
		self.observable.changed(self.request)
		
		self.assertEqualsWS(self.OAIPMH % """
<request verb="ListSets">http://server:9000/path/to/oai</request>
 <ListSets>
   <set><setSpec>some:name:id_0</setSpec><setName>Some Name</setName></set>
   <set><setSpec>some:name:id_1</setSpec><setName>Some Name</setName></set>
 </ListSets>""", self.stream.getvalue())
 		self.assertFalse('<resumptionToken' in self.stream.getvalue())

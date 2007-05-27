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
from meresco.queryserver.observers.oaicomponent import OaiComponent
from cq2utils.observable import Observable

class OaiComponentTest(OaiTestCase):
	
	def getSubject(self):
		return OaiComponent()
	
	def testChaining(self):
		self.request.args = {'verb': ['Identify']}
		self.observable.changed(self.request)
		self.assertTrue(self.stream.getvalue().find('<Identify>') >-1)
	
	def testChainingEndsUpInSink(self):
		self.assertBadArgument({'verb': ['Nonsense']}, 'Argument value "Nonsense" for verb illegal.')
		
	def testComponentSeemsOne(self):
		pass #KVS:!! dit testen is voor mij 10x zo veel werk als de code. Ik houd me aanbevolen voor een goed actieplan!

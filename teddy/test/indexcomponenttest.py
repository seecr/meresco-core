## begin license ##
#
#    Teddy is the name for Seek You Too's Search Appliance.
#    Copyright (C) 2006 Stichting SURF. http://www.surf.nl
#    Copyright (C) 2006-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of Teddy.
#
#    Teddy is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Teddy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Teddy; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
from cq2utils.cq2testcase import CQ2TestCase
from cq2utils.calltrace import CallTrace
from cq2utils.component import Notification
from indexcomponent import IndexComponent
from xml2document import TEDDY_NS, Xml2Document
from cq2utils.observable import Observable
from amara import binderytools

FIELDS = binderytools.bind_string("""<xmlfields xmlns:teddy="%s">
	<field1>this is field1</field1>
	<untokenizedField teddy:tokenize="false">this should not be tokenized</untokenizedField>
</xmlfields>""" % TEDDY_NS).xmlfields

class IndexComponentTest(CQ2TestCase):
	def setUp(self):
		CQ2TestCase.setUp(self)
		self.index = CallTrace("Index")
		self.subject = IndexComponent(self.index)
		
		self.notification = Notification()
		self.notification.method = "add"
		self.notification.id = "anId-123"
		self.notification.partName = "xmlfields"
		self.notification.document = Xml2Document().create(self.notification.id, FIELDS)
		
		self.observable = Observable()
		self.observable.addObserver(self.subject)
	
	def testAdd(self):
		self.observable.changed(self.notification)
		self.assertEquals(2,len(self.index.calledMethods))
		self.assertEquals("deleteID('anId-123')", str(self.index.calledMethods[0]))
		self.assertEquals('addToIndex(<document.Document>)', str(self.index.calledMethods[1]))
		
	def testDelete(self):
		self.notification.method = "delete"
		self.observable.changed(self.notification)
		
		self.assertEquals(1,len(self.index.calledMethods))
		self.assertEquals("deleteID('anId-123')", str(self.index.calledMethods[0]))
		
	def testUndo(self):
		class MyObserver:
			def notify(self, *args):
				raise Exception('uhoh')
			def undo(self, *args, **kwargs):
				pass
		self.observable.addObserver(MyObserver())
		
		try:
			self.observable.changed(self.notification)
			self.fail()
		except Exception, e:
			self.assertEquals('uhoh', str(e))
		self.assertEquals(3,len(self.index.calledMethods))
		self.assertEquals("deleteID('anId-123')", str(self.index.calledMethods[0]))
		self.assertEquals('addToIndex(<document.Document>)', str(self.index.calledMethods[1]))
		self.assertEquals("deleteID('anId-123')", str(self.index.calledMethods[2]))

	

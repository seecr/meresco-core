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

from cq2utils.cq2testcase import CQ2TestCase

from meresco.teddy.fields2xmlcomponent import Fields2XmlComponent
from cq2utils.component import Notification
from meresco.teddy.xml2document import TEDDY_NS
from amara import binderytools

FIELDS = """<fields>
	<field name="field1">this is field1</field>
	<field name="untokenizedField" tokenize="false">this should not be tokenized</field>
</fields>"""
XMLFIELDS = """<xmlfields xmlns:teddy="%(teddyns)s" teddy:skip="true">
	<field1>this is field1</field1>
	<untokenizedField  teddy:tokenize="false">this should not be tokenized</untokenizedField>
</xmlfields>
""" % {'teddyns': TEDDY_NS}

class Fields2XmlComponentTest(CQ2TestCase):
	def setUp(self):
		CQ2TestCase.setUp(self)
		self.component = Fields2XmlComponent()
		self.component.addObserver(self)
		self.notifications = []
	
	def notify(self, aNotification):
		self.notifications.append(aNotification)
	
	def testNotify(self):
		record = Notification('add', 'id', 'fields')
		record.payload = FIELDS
		self.component.notify(record)
		self.assertEquals(1, len(self.notifications))
		newNotification = self.notifications[0]
		self.assertEquals(record.id, newNotification.id)
		self.assertEquals('xmlfields', newNotification.partName)
		self.assertEqualsWS(XMLFIELDS, newNotification.payload.xml())
	
	def testNotifyIgnored(self):
		record = Notification('add', 'id', 'nofields')
		self.component.notify(record)
		self.assertEquals(0, len(self.notifications))

	def testIndexSkipField(self):
		record = Notification('add', 'id', 'fields')
		record.payload = """<fields><field name="a">A</field><field name="original:lom">&lt;lom/&gt;</field></fields>"""
		self.component.notify(record)
		self.assertEquals(1, len(self.notifications))
		newNotification = self.notifications[0]
		self.assertEquals("""<xmlfields xmlns:teddy="%s" teddy:skip="true"><a>A</a></xmlfields>""" % TEDDY_NS, newNotification.payload.xml())

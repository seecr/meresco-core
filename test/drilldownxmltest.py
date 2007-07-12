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

from StringIO import StringIO

from cq2utils.cq2testcase import CQ2TestCase

from meresco.components.http.drilldownxml import DrillDownXml

class DrillDownXmlTest(CQ2TestCase):
	
	def testOne(self):
		self._arguments = {"x-meresco-drilldown": ["field0:1,field1:2,field2:3"]}
		result = StringIO()
		self.write = result.write
		drillDownXml = DrillDownXml(self)
		drillDownXml.writeExtraResponseData(self)
		self.assertEquals([('field0', '1'), ('field1', '2'), ('field2', '3')], self.tuples)
		self.assertEqualsWS("""<drilldown>
<field name="field0">
	<value count="14">value0_0</value>
</field>
<field name="field1">
	<value count="13">value1_0</value>
	<value count="11">value1_1</value>
</field>
<field name="field2">
	<value count="3">value2_0</value>
	<value count="2">value2_1</value>
	<value count="1">value2_2</value>
</field></drilldown>""", result.getvalue())
		
	def process(self, tuples):
		self.tuples = tuples
		return [
			('field0', [('value0_0', 14)]),
			('field1', [('value1_0', 13), ('value1_1', 11)]),
			('field2', [('value2_0', 3), ('value2_1', 2), ('value2_2', 1)])]

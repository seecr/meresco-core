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
from cq2utils.calltrace import CallTrace

from meresco.components.drilldown.srudrilldownadapter import SRUDrillDownAdapter, SRUTermDrillDown, SRUFieldDrillDown

class SRUDrillDownAdapterTest(CQ2TestCase):
    
    def testOne(self):
        class MockedImpl:
            def extraResponseData(sself, webRequest, hits):
                yield "<tag>"
                yield "something</tag>"
                
        adapter = SRUDrillDownAdapter([MockedImpl, MockedImpl])
        result = list(adapter.extraResponseData("ignored_webRequest", "ignored_hits"))
        self.assertEqualsWS([
            '<dd:drilldown xmlns:dd="something/xsd/drilldown.xsd">',
            '<tag>', 'something</tag>',
            '<tag>', 'something</tag>',
            '</dd:drilldown>'], result)

class SRUTermDrillDownTest(CQ2TestCase):

    def testSRUTermDrillDown(self):
        self._arguments = {"x-term-drilldown": ["field0:1,field1:2,field2:3"]}
        adapter = SRUTermDrillDown()
        adapter.addObserver(self)
        hits = CallTrace("Hits")
        hits.returnValues['docNumbers'] = "Hits are simply passed"
        result = adapter.extraResponseData(self, hits)
        self.assertEqualsWS("""<dd:term-drilldown><dd:navigator name="field0">
    <dd:item count="14">value0_0</dd:item>
</dd:navigator>
<dd:navigator name="field1">
    <dd:item count="13">value1_0</dd:item>
    <dd:item count="11">value1_1</dd:item>
</dd:navigator>
<dd:navigator name="field2">
    <dd:item count="3">value2_0</dd:item>
    <dd:item count="2">value2_1</dd:item>
    <dd:item count="1">value2_2</dd:item>
</dd:navigator></dd:term-drilldown>""", "".join(result))
        self.assertEquals([('field0', 1), ('field1', 2), ('field2', 3)], list(self.processed_tuples))
        self.assertEquals("Hits are simply passed", self.processed_hits)
        
    def drillDown(self, hits, tuples):
        self.processed_hits = hits
        self.processed_tuples = tuples
        return [
            ('field0', [('value0_0', 14)]),
            ('field1', [('value1_0', 13), ('value1_1', 11)]),
            ('field2', [('value2_0', 3), ('value2_1', 2), ('value2_2', 1)])]

class SRUFieldDrillDownTest(CQ2TestCase):

    def testSRUParamsAndXMLOutput(self):
        self._arguments = {"x-field-drilldown": ["term"], 'x-field-drilldown-fields': ['field0,field1'], 'query': ['original']}
        adapter = SRUFieldDrillDown()
        adapter.drillDown = self.drillDown
        
        self.drillDownCall = None
        result = adapter.extraResponseData(self, "ignored_hits")
        self.assertEqualsWS("""<dd:field-drilldown>
<dd:field name="field0">5</dd:field>
<dd:field name="field1">10</dd:field></dd:field-drilldown>""", "".join(result))

        self.assertEquals(('original', 'term', ['field0', 'field1']), self.drillDownCall)
        
    def drillDown(self, query, term, fields):
        self.drillDownCall = (query, term, fields)
        return [('field0', 5),('field1', 10)]
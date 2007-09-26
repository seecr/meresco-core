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
from unittest import TestCase

from cq2utils.calltrace import CallTrace
from amara import binderytools

from meresco.components.drilldown.drilldownfilters import DrilldownUpdateFieldFilter, DrilldownRequestFieldFilter
from meresco.framework.observable import Observable

class DrilldownFiltersTest(TestCase):

    def testDrilldownUpdateFieldFilter(self):
        data = binderytools.bind_string("""<xmlfields>
    <field_0>term_0</field_0>
    <field_1>term_1</field_1>
    <field_2>term_2</field_2>
</xmlfields>""")

        drilldownUpdateFieldFilter = DrilldownUpdateFieldFilter(['xmlfields.field_0', 'xmlfields.field_1'])
        observer = CallTrace('Observer')

        drilldownUpdateFieldFilter.addObserver(observer)

        drilldownUpdateFieldFilter.add("id", "partName", data.xmlfields)

        self.assertEquals(1, len(observer.calledMethods))
        self.assertEquals(["id", "partName"], observer.calledMethods[0].arguments[:2])

        resultXml = observer.calledMethods[0].arguments[2]
        self.assertEquals(1, len(resultXml.xml_xpath('field_0')))
        self.assertEquals(1, len(resultXml.xml_xpath('field_0__untokenized__')))
        self.assertEquals(1, len(resultXml.xml_xpath('field_1')))
        self.assertEquals(1, len(resultXml.xml_xpath('field_1__untokenized__')))
        self.assertEquals(1, len(resultXml.xml_xpath('field_2')))
        self.assertEquals(0, len(resultXml.xml_xpath('field_2__untokenized__')))

        node = resultXml.xml_xpath("//field_0__untokenized__")[0]
        self.assertEquals(1, len(node.attributes))
        self.assertEquals('<field_0__untokenized__ xmlns:teddy="http://www.cq2.nl/teddy" teddy:tokenize="false">term_0</field_0__untokenized__>', node.xml())

    def testDrilldownUpdateFieldFilterDeep(self):
        data = binderytools.bind_string("""<level_0><level_1><level_2>term_0</level_2></level_1></level_0>""")

        drilldownUpdateFieldFilter = DrilldownUpdateFieldFilter(['level_0.level_1.level_2'])
        observer = CallTrace('Observer')

        drilldownUpdateFieldFilter.addObserver(observer)

        drilldownUpdateFieldFilter.add("id", "partName", data.level_0)

        self.assertEquals(1, len(observer.calledMethods))
        self.assertEquals(["id", "partName"], observer.calledMethods[0].arguments[:2])

        resultXml = observer.calledMethods[0].arguments[2]
        self.assertEquals(1, len(resultXml.xml_xpath('/level_0/level_1/level_2')))
        self.assertEquals(1, len(resultXml.xml_xpath('/level_0/level_1/level_2__untokenized__')))

        node = resultXml.xml_xpath("/level_0/level_1/level_2__untokenized__")[0]

        self.assertEquals(1, len(node.attributes))
        self.assertEquals('<level_2__untokenized__ xmlns:teddy="http://www.cq2.nl/teddy" teddy:tokenize="false">term_0</level_2__untokenized__>', node.xml())

    def testDrilldownUpdateFieldFilterDeepWithNamespace(self):
        data = binderytools.bind_string("""<y:level_0 xmlns:y="http://localhost/y" xmlns:x="http://localhost/s"><x:level_1><x:level_2>term_0</x:level_2></x:level_1></y:level_0>""")

        drilldownUpdateFieldFilter = DrilldownUpdateFieldFilter(['level_0.level_1.level_2'])
        observer = CallTrace('Observer')

        drilldownUpdateFieldFilter.addObserver(observer)

        drilldownUpdateFieldFilter.add("id", "partName", data.level_0)

        self.assertEquals(1, len(observer.calledMethods))
        self.assertEquals(["id", "partName"], observer.calledMethods[0].arguments[:2])

        resultXml = observer.calledMethods[0].arguments[2]
        self.assertEquals(1, len(resultXml.xml_xpath('/y:level_0/x:level_1/x:level_2')))
        self.assertEquals(1, len(resultXml.xml_xpath('/y:level_0/x:level_1/x:level_2__untokenized__')), resultXml.xml())

        node = resultXml.xml_xpath("/y:level_0/x:level_1/x:level_2__untokenized__")[0]

        self.assertEquals(1, len(node.attributes))
        self.assertEquals('<x:level_2__untokenized__ xmlns:x="http://localhost/s" xmlns:teddy="http://www.cq2.nl/teddy" teddy:tokenize="false">term_0</x:level_2__untokenized__>', node.xml())


    def testDrilldownRequestFieldFilter(self):
        requestFilter = DrilldownRequestFieldFilter()
        observer = CallTrace('Observer')
        observer.returnValues["drilldown"] = [("field_0__untokenized__", "Passed Along Result")]
        requestFilter.addObserver(observer)
        result = requestFilter.drilldown("Passed Along Input", [("field_0", 0), ("field_1", 1)])
        self.assertEquals(1, len(observer.calledMethods))
        method = observer.calledMethods[0]
        self.assertEquals("Passed Along Input", method.arguments[0])
        self.assertEquals([("field_0__untokenized__", 0), ("field_1__untokenized__", 1)], list(method.arguments[1]))
        self.assertEquals([("field_0", "Passed Along Result")], list(result))

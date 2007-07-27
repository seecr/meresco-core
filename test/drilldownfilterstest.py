from unittest import TestCase

from cq2utils.calltrace import CallTrace
from amara import binderytools

from meresco.components.drilldown.drilldownfilters import DrillDownUpdateFieldFilter, DrillDownRequestFieldFilter
from meresco.framework.observable import Observable

class DrillDownFiltersTest(TestCase):

    def testDrillDownUpdateFieldFilter(self):
        data = binderytools.bind_string("""<xmlfields>
    <field_0>term_0</field_0>
    <field_1>term_1</field_1>
    <field_2>term_2</field_2>
</xmlfields>""")

        drillDownUpdateFieldFilter = DrillDownUpdateFieldFilter(['field_0', 'field_1'])
        observer = CallTrace('Observer')

        drillDownUpdateFieldFilter.addObserver(observer)

        drillDownUpdateFieldFilter.add("id", "partName", data.xmlfields)

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

    def testDrillDownRequestFieldFilter(self):
        requestFilter = DrillDownRequestFieldFilter()
        observer = CallTrace('Observer')
        observer.returnValues["drillDown"] = [("field_0__untokenized__", "Passed Along Result")]
        requestFilter.addObserver(observer)
        result = requestFilter.drillDown("Passed Along Input", [("field_0", 0), ("field_1", 1)])
        self.assertEquals(1, len(observer.calledMethods))
        method = observer.calledMethods[0]
        self.assertEquals("Passed Along Input", method.arguments[0])
        self.assertEquals([("field_0__untokenized__", 0), ("field_1__untokenized__", 1)], list(method.arguments[1]))
        self.assertEquals([("field_0", "Passed Along Result")], list(result))
from unittest import TestCase

from cq2utils.component import Notification
from cq2utils.calltrace import CallTrace
from amara import binderytools

from meresco.components.drilldown.drilldownfieldcomponent import DrilldownFieldComponent
from meresco.framework.observable import Observable

DATA = """<xmlfields>
    <field_0>term_0</field_0>
    <field_1>term_1</field_1>
    <field_2>term_2</field_2>
</xmlfields>"""

class DrilldownFieldComponentTest(TestCase):

    def testIfItWorks(self):
        data = binderytools.bind_string(DATA)

        observable = Observable()
        drilldownFieldComponent = DrilldownFieldComponent(['field_0', 'field_1'])
        observer = CallTrace('Observer')

        observable.addObserver(drilldownFieldComponent)
        drilldownFieldComponent.addObserver(observer)

        notification = Notification()
        notification.method = "add"
        notification.payload = data.xmlfields
        observable.changed(notification)

        self.assertEquals(1, len(observer.calledMethods))

        resultXml = observer.calledMethods[0].arguments[0].payload
        self.assertEquals(1, len(resultXml.xml_xpath('field_0')))
        self.assertEquals(1, len(resultXml.xml_xpath('field_0__untokenized__')))
        self.assertEquals(1, len(resultXml.xml_xpath('field_1')))
        self.assertEquals(1, len(resultXml.xml_xpath('field_1__untokenized__')))
        self.assertEquals(1, len(resultXml.xml_xpath('field_2')))
        self.assertEquals(0, len(resultXml.xml_xpath('field_2__untokenized__')))

        node = resultXml.xml_xpath("//field_0__untokenized__")[0]
        self.assertEquals(1, len(node.attributes))
        self.assertEquals('<field_0__untokenized__ xmlns:teddy="http://www.cq2.nl/teddy" teddy:tokenize="true">term_0</field_0__untokenized__>', node.xml())


#<xmlfields>
    #<field_0>term_0</field_0>
    #<field_0__untokenized__ teddy:tokenize="false">term_0</field_0__untokenized__>
    #<field_1>term_1</field_1>
    #<field_1__untokenized__ teddy:tokenize="false">term_1</field_1__untokenized__>
#</xmlfields>

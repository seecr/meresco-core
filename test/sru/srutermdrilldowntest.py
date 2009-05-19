
from cq2utils import CQ2TestCase, CallTrace

from merescocore.components.drilldown import SRUTermDrilldown, DRILLDOWN_HEADER, DRILLDOWN_FOOTER, DEFAULT_MAXIMUM_TERMS


class SRUTermDrilldownTest(CQ2TestCase):
    def testSRUTermDrilldown(self):
        sruTermDrilldown = SRUTermDrilldown()

        observer = CallTrace("Drilldown")
        observer.returnValues['docsetFromQuery'] = 'docset'
        observer.returnValues['drilldown'] = [
                ('field0', [('value0_0', 14)]),
                ('field1', [('value1_0', 13), ('value1_1', 11)]),
                ('field2', [('value2_0', 3), ('value2_1', 2), ('value2_2', 1)])]

        sruTermDrilldown.addObserver(observer)
        cqlAbstractSyntaxTree = 'cqlAbstractSyntaxTree'

        result = sruTermDrilldown.extraResponseData(cqlAbstractSyntaxTree, x_term_drilldown=["field0:1,field1:2,field2"])
        self.assertEqualsWS(DRILLDOWN_HEADER + """<dd:term-drilldown><dd:navigator name="field0">
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
</dd:navigator></dd:term-drilldown></dd:drilldown>""", "".join(result))
        self.assertEquals(['docsetFromQuery', 'drilldown'], [m.name for m in observer.calledMethods])
        self.assertEquals('cqlAbstractSyntaxTree', observer.calledMethods[0].args[0])
        self.assertEquals([('field0', 1, False), ('field1', 2, False), ('field2', DEFAULT_MAXIMUM_TERMS, False)], list(observer.calledMethods[1].args[1]))


    def testEchoedExtraRequestData(self):
        component =SRUTermDrilldown()

        result = "".join(list(component.echoedExtraRequestData(x_term_drilldown=['field0,field1'], version='1.1')))
        
        self.assertEqualsWS(DRILLDOWN_HEADER \
        + """<dd:term-drilldown>field0,field1</dd:term-drilldown>"""\
        + DRILLDOWN_FOOTER, result)
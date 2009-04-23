## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2009 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
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

from cq2utils import CQ2TestCase, CallTrace
from merescocore.framework import be
from merescocore.components.drilldown.srudrilldownadapter import SRUTermDrilldown, SRUFieldDrilldown, DRILLDOWN_HEADER, DRILLDOWN_FOOTER, decorateWith, _wrapInDrilldownTag

from cqlparser.cqlcomposer import compose as cqlCompose


class DecorateWithTest(CQ2TestCase):
    @staticmethod
    def gen(yieldSomething=True):
        if yieldSomething :
            yield 'something'
    
    def testDecorateWith(self):
        self.assertEquals("something", "".join(gen()))
        self.assertEquals("", "".join(gen(yieldSomething=False)))

        @decorateWith("This is ", ", isn't it?")
        def tobedecorated1(*args, **kwargs):
            return gen(*args, **kwargs)
        self.assertEquals("This is something, isn't it?", "".join(tobedecorated1()))
        self.assertEquals("", "".join(tobedecorated1(yieldSomething=False)))

    def testWrapInDrilldownTag(self):
        @wrapInDrilldownTag
        def tobedecorated(*args, **kwargs):
            return gen(*args, **kwargs)
        self.assertEqauls(DRILLDOWN_HEADER + "something" + DRILLDOWN_FOOTER, "".join(tobedecorated()))
        self.assertEquals("", "".join(tobedecorated(yieldSomething=False)))


class SRUTermDrilldownTest(CQ2TestCase):

    def testSRUTermDrilldown(self):
        sruTermDrilldown = SRUTermDrilldown()
        sruTermDrilldown.addObserver(self)
        hits = ['recordId:1', 'recordId:2']
        cqlAbstractSyntaxTree = 'cqlAbstractSyntaxTree'

        result = sruTermDrilldown.extraResponseData(cqlAbstractSyntaxTree, x_term_drilldown=["field0:1,field1:2,field2:3"])
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
        self.assertEquals([('field0', 1, False), ('field1', 2, False), ('field2', 3, False)], list(self.processed_tuples))
        self.assertEquals('cqlAbstractSyntaxTree', self.processed_ast)

    def testSRUTermDrilldownNoMaximums(self):
        sruTermDrilldown = SRUTermDrilldown()
        sruTermDrilldown.addObserver(self)
        list(sruTermDrilldown.extraResponseData(cqlAbstractSyntaxTree=[], x_term_drilldown=["field0,field1,field2"]))
        self.assertEquals([('field0', 10, False), ('field1', 10, False), ('field2', 10, False)], list(self.processed_tuples))

    def docsetFromQuery(self, ast):
        self.processed_ast = ast
        return 'row'

    def drilldown(self, row, tuples):
        self.processed_row = row
        self.processed_tuples = tuples
        return [
            ('field0', [('value0_0', 14)]),
            ('field1', [('value1_0', 13), ('value1_1', 11)]),
            ('field2', [('value2_0', 3), ('value2_1', 2), ('value2_2', 1)])]
            
    def testEchoedExtraRequestData(self):
        sruTermDrilldown = SRUTermDrilldown()
        result = sruTermDrilldown.echoedExtraRequestData(x_term_drilldown=['dummy'])
        self.assertEqualsWS(DRILLDOWN_HEADER + """<dd:term-drilldown>dummy</dd:term-drilldown></dd:drilldown>""", "".join(result))


class SRUFieldDrilldownTest(CQ2TestCase):

    def testSRUParamsAndXMLOutput(self):
        sruFieldDrilldown = SRUFieldDrilldown()
        sruFieldDrilldown.drilldown = self.drilldown

        self.drilldownCall = None
        result = sruFieldDrilldown.extraResponseData(x_field_drilldown=['term'], x_field_drilldown_fields=['field0,field1'], query='original')
        self.assertEqualsWS(DRILLDOWN_HEADER + """<dd:field-drilldown>
<dd:field name="field0">5</dd:field>
<dd:field name="field1">10</dd:field></dd:field-drilldown></dd:drilldown>""", "".join(result))

        self.assertEquals(('original', 'term', ['field0', 'field1']), self.drilldownCall)

    def drilldown(self, query, term, fields):
        self.drilldownCall = (query, term, fields)
        return [('field0', 5),('field1', 10)]

    def testDrilldown(self):
        adapter = SRUFieldDrilldown()
        observer = CallTrace("Observer")
        observer.returnValues["executeCQL"] = (16, range(16))
        adapter.addObserver(observer)
        result = list(adapter.drilldown('original', 'term', ['field0', 'field1']))

        self.assertEquals(2, len(observer.calledMethods))
        self.assertEquals("executeCQL(cqlAbstractSyntaxTree=<class CQL_QUERY>)", str(observer.calledMethods[0]))
        self.assertEquals("(original) and field0=term",  cqlCompose(observer.calledMethods[0].kwargs['cqlAbstractSyntaxTree']))
        self.assertEquals([("field0", 16), ("field1", 16)], result)

    def testEchoedExtraRequestData(self):
        d = SRUFieldDrilldown()
        result = "".join(d.echoedExtraRequestData(x_field_drilldown=['term'], x_field_drilldown_fields = ['field0,field1'], otherArgument=['ignored']))
        self.assertEquals(DRILLDOWN_HEADER + '<dd:field-drilldown>term</dd:field-drilldown><dd:field-drilldown-fields>field0,field1</dd:field-drilldown-fields></dd:drilldown>', result)


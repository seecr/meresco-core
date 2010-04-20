# -*- coding: utf-8 -*-
## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
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
from meresco.core import be, decorateWith
from meresco.components.drilldown import SRUFieldDrilldown, DRILLDOWN_HEADER, DRILLDOWN_FOOTER

from cqlparser import parseString

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
        self.assertEquals(parseString("(original) and field0=term"),  observer.calledMethods[0].kwargs['cqlAbstractSyntaxTree'])
        self.assertEquals([("field0", 16), ("field1", 16)], result)

    def testEchoedExtraRequestData(self):
        d = SRUFieldDrilldown()
        result = "".join(d.echoedExtraRequestData(x_field_drilldown=['term'], x_field_drilldown_fields = ['field0,field1'], otherArgument=['ignored']))
        self.assertEquals(DRILLDOWN_HEADER + '<dd:field-drilldown>term</dd:field-drilldown><dd:field-drilldown-fields>field0,field1</dd:field-drilldown-fields></dd:drilldown>', result)


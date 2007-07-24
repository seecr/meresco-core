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

from meresco.components.fields2xmlcomponent import Fields2XmlComponent
from cq2utils.calltrace import CallTrace
from meresco.components.xml2document import TEDDY_NS
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
        self.observer = CallTrace("Observer")
        self.component.addObserver(self.observer)
        self.notifications = []
    
    def testAdd(self):
        self.component.add("id", "fields", FIELDS)
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEquals(["id", "xmlfields"], self.observer.calledMethods[0].arguments[:2])
        self.assertEqualsWS(XMLFIELDS, self.observer.calledMethods[0].arguments[2].xml())
    
    def testAddIgnoresNonFields(self):
        self.component.add('id', 'this_is_not_fields', "also ignored")
        self.assertEquals(0, len(self.observer.calledMethods))

    def testIndexSkipField(self):
        self.component.add('id', 'fields', """<fields><field name="a">A</field><field name="original:lom">&lt;lom/&gt;</field></fields>""")
        
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEqualsWS("""<xmlfields xmlns:teddy="%s" teddy:skip="true"><a>A</a></xmlfields>""" % TEDDY_NS, self.observer.calledMethods[0].arguments[2].xml())

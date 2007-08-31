## begin license ##
#
#    LOREnet is a tool for sharing knowledge within and beyond the walls of
#    your own school or university.
#    Copyright (C) 2006-2007 Stichting SURF. http://www.surf.nl
#    Copyright (C) 2006-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of LOREnet.
#
#    LOREnet is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    LOREnet is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with LOREnet; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
from cq2utils.cq2testcase import CQ2TestCase
from cq2utils.calltrace import CallTrace
from cq2utils.xmlutils.xmlrewrite import XMLRewrite

from StringIO import StringIO
from lxml.etree import parse, tostring, XMLParser
from difflib import unified_diff

from re import match
from os import remove

from meresco.components import Crosswalk
from meresco.components.crosswalk import rewriteRules
from meresco.components.xml_generic import Validate


def readRecord(name):
    return open('xml_generic/lxml_based/data/' + name)

class CrosswalkTest(CQ2TestCase):

    def setUp(self):
        CQ2TestCase.setUp(self)
        self.crosswalk = Crosswalk('LOMv1.0')
        self.observer = CallTrace()
        self.crosswalk.addObserver(self.observer)

    def testOne(self):
        list(self.crosswalk.unknown('crosswalk', 'id', 'partname', parse(readRecord('imsmd_v1p2-1.xml'), XMLParser(remove_blank_text=True))))
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEquals(3, len(self.observer.calledMethods[0].arguments))
        arguments = self.observer.calledMethods[0].arguments
        self.assertEquals("id", arguments[0])
        self.assertEquals("LOMv1.0", arguments[1])
        self.assertTrue("XMLRewrite" in str(arguments[2]))

    def testValidate(self):
        validate = Validate()
        validate.unknown('methodname', 'id', 'part', parse(readRecord('lom-cc-nbc.xml')))
        #notification = Notification(method = 'add', id=None, partName='LOMv1.0', payload=readRecord('lom-cc-nbc.xml'))
        try:
            validate.unknown('methodname', 'id', 'part', parse(readRecord('lom-cc-nbc.xml')))
        except Exception, e:
            self.fail(e)


        return
        notification = Notification(method = 'add', id=None, partName='metadata', payload=readRecord('imsmd_v1p2-1.xml'))
        try:
            self.validator.notify(notification)
            self.fail('must raise exception')
        except Exception, e:
            self.assertEquals("<string>:2:ERROR:SCHEMASV:SCHEMAV_CVC_ELT_1: Element '{http://dpc.uba.uva.nl/schema/lom/triplel}lom': No matching global declaration available for the validation root.", str(e))

    def testTripleLExample(self):
        notification = Notification(method = 'add', id=None, partName='IMS', payload=readRecord('triple-lrecord.xml'))
        try:
            self.plugin.notify(notification)
        except Exception, e:
            for n, line in enumerate(self.message.payload.split('\n')):
                print n+1, line
            raise

    def testDoNotActOnOther(self):
        notification = Notification(method = 'add', id=None, partName='Other', payload=readRecord('imsmd_v1p2-1.xml'))
        self.plugin.notify(notification)
        self.assertFalse(hasattr(self, 'message'))

    def testNormalize(self):
        notification = Notification(method = 'add', id=None, partName='metadata', payload=readRecord('triple-lrecord.xml'))
        self.plugin.notify(notification)
        self.assertFalse('2006-11-28 19:00' in self.message.payload)


    def testReplacePrefix(self):
        rules = [('classification/taxonPath/taxon/entry', 'imsmd:classification/imsmd:taxonpath/imsmd:taxon/imsmd:entry', ('imsmd:langstring/@xml:lang', 'imsmd:langstring'), '<string language="%s">%s</string>',
        [('\s*\d+\s*(\w+)', '%s', (str,))])]
        newRules = rewriteRules('imsmd', '', rules)
        self.assertEquals(rules[0][-1], newRules[0][-1])

    def testXPathNodeTest(self):
        x = """
        <x>
            <y>
                <p>
                    <q>selector</q>
                </p>
                <z>aap</z>
            </y>
            <y>
                <p>
                    <q>not-selector</q>
                </p>
                <z>mies</z>
            </y>
        </x>
        """
        tree = parse(StringIO(x))
        result = tree.xpath('y')
        self.assertEquals(2, len(result))
        result = tree.xpath('y[p/q="selector"]')
        self.assertEquals(1, len(result))
        self.assertEquals('y', result[0].tag)

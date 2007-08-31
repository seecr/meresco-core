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
from StringIO import StringIO
from lxml.etree import parse, tostring, XMLParser
from difflib import unified_diff

from re import match
from os import remove

from meresco.components import Crosswalk
from meresco.components.crosswalk import rewriteRules
from meresco.components.xml_generic import Validate


def readRecord(name):
    return open('data/' + name).read()

class CrosswalkTest(CQ2TestCase):

    def setUp(self):
        CQ2TestCase.setUp(self)
        class Interceptor:
            def notify(inner, notification): self.message = notification
            def undo(*args): pass
        self.plugin = Crosswalk()
        self.plugin.addObserver(Interceptor())
        self.validator = IeeeLomValidateComponent()
        self.plugin.addObserver(self.validator)

    def tearDown(self):
        CQ2TestCase.tearDown(self)
        if hasattr(self, 'message'): del self.message

    def testOne(self):
        notification = Notification(method = 'add', id=None, partName='metadata', payload=readRecord('imsmd_v1p2-1.xml'))
        self.plugin.notify(notification)
        self.assertTrue(hasattr(self, 'message'))

    def testValidate(self):
        notification = Notification(method = 'add', id=None, partName='LOMv1.0', payload=readRecord('lom-cc-nbc.xml'))
        try:
            self.validator.notify(notification)
        except Exception, e:
            self.fail(e)
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

    def testTripleLRecords(self):
        self.assertRecord('triple_l:oai:triple-l:217132')
        self.assertRecord('triple_l:oai:triple-l:217134')
        self.assertRecord('triple_l:oai:triple-l:210219')
        self.assertRecord('triple_l:oai:triple-l:209753')

    def testWURTVRecords(self):
        self.assertRecord('wurtv:oai:triple-l:02a7a352-907b-4f66-8d15-2c1d1ffbd4aa')

    def testLUMCRecords(self):
        self.assertRecord('lumc:69')
        self.assertRecord('lumc:24')

    def testUtRecords(self):
        self.assertRecord('utlore:oai:lorenet:408')
        self.assertRecord('utlore:oai:lorenet:201')

    def testGroenlomRecords(self):
        self.assertRecord('groenlom:oai:groenkennisnet.org:6426112')

    def testSVPRecords(self):
        self.assertRecord('svp:VPOAI:1')

    def testSchoolVanDeToekomstRecords(self):
        self.assertRecord('svdt_org:oai:repository.kenict.org:id:49')

    def testDeltionRecords(self):
        self.assertRecord('deltion_nl:oai:repository.kenict.org:id:75')

    def testFontysRecords(self):
        self.assertRecord('fontyselo:oai:prefix:0458cc8d30194c8d99534659cae8e014')
        self.assertRecord('fontyselo:oai:prefix:e2b22198e99f4c828b55527216480256')
        self.assertRecord('fontyselo:oai:fontys:38aa67ab30894df18f8c91ba33a24899')

    def assertRecord(self, id):
        inputRecord = readRecord('%s.xml' % id)
        sollRecord = tostring(parse(open('data/%s.LOMv1.0.xml' % id), XMLParser(remove_blank_text=True)), pretty_print = True)
        notification = Notification(method = 'add', id=None, partName='metadata', payload = inputRecord)
        try:
            self.plugin.notify(notification)
        except Exception, e:
            if hasattr(self, 'message'):
                for nr, line in enumerate(self.message.payload.split('\n')): print nr, line
            raise
        self.assertTrue(hasattr(self, 'message'))
        diffs = list(unified_diff(self.message.payload.split('\n'), sollRecord.split('\n'), fromfile='ist', tofile='soll', lineterm=''))
        self.assertFalse(diffs, '\n' + '\n'.join(diffs))

    def testReadRulesFromDir(self):
        f = open('/tmp/prefix1.rules', 'w')
        f.write("""
inputNamespace='namespaceURI'
rootTagName='lom'
defaultNameSpace='http://ltsc.ieee.org/xsd/LOM'
vocabDict={}
rules=[]
""")
        f.close()
        try:
            crosswalk = CrosswalkComponent(rulesDir='/tmp')
            rules = crosswalk.ruleSet['namespaceURI']
            self.assertEquals('http://ltsc.ieee.org/xsd/LOM', rules['defaultNameSpace'])
        finally:
            remove('/tmp/prefix1.rules')

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

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
        self.crosswalk = Crosswalk('theXmlRecord')
        self.validate = Validate(['metadata'])
        self.crosswalk.addObserver(self.validate)
        self.observer = CallTrace()
        self.validate.addObserver(self.observer)

    def testDoesItReallyWorkThatWayOrWhyIsItNecessaryToPrettyPrintAndReparseTheXmlSixQuestionMarks(self):
        xml = """<lom xmlns="http://ltsc.ieee.org/xsd/LOM">
  <general>
    <identifier>
      <catalog>Naam van de repository of instelling</catalog>
      <entry>Identificatiecode/identifier/etc, uniek binnen catalog</entry>
    </identifier>
    <title>
      <string language="x-none">Een titel</string>
    </title>
    <language>
                        nl
                </language>
    <description/>
    <keyword/>
    <aggregationLevel>
      <value>1</value>
    </aggregationLevel>
  </general>
  <lifeCycle>
    <version>
      <string language="x-none">v1.0beta-rc01-with-fixes</string>
    </version>
    <status>
      <source>LOMv1.0</source>
      <value>final</value>
    </status>
    <contribute>
      <role>
        <source>LOMv1.0</source>
        <value>author</value>
      </role>
      <entity>BEGIN:VCARD
FN:Suilen, A.
END:VCARD</entity>
      <date>
        <dateTime>2007-12-31T13:31</dateTime>
      </date>
    </contribute>
  </lifeCycle>
  <metaMetadata>
    <metadataSchema>lorelom</metadataSchema>
    <contribute>
      <role>
        <source>LOMv1.0</source>
        <value>creator</value>
      </role>
      <entity>BEGIN:VCARD
FN;parameter:Suilen, A.
VERSION:3.0
x;aap:mies
END:VCARD</entity>
      <date>
        <dateTime>2007-01-01T08:32</dateTime>
      </date>
    </contribute>
  </metaMetadata>
  <technical>
    <format>!3e#s$p&amp;l.a+n-k^j_e/a_a+p#</format>
    <location>http://my.system.nl/hier/staat/het.zip</location>
    <location>http://my.system.nl/hier/staat/nog.zip</location>
    <location>http://my.system.nl/hier/staat/meer.zip</location>
  </technical>
  <educational>
    <learningResourceType>
      <source>LOMv1.0</source>
      <value>table</value>
    </learningResourceType>
    <context>
      <source>LOMv1.0</source>
      <value>higher education</value>
    </context>
  </educational>
  <rights>
    <cost>
      <source>LOMv1.0</source>
      <value>no</value>
    </cost>
    <copyrightAndOtherRestrictions>
      <source>CCv2.5</source>
      <value>by-nc-nd</value>
    </copyrightAndOtherRestrictions>
    <description/>
  </rights>
  <annotation>
    <entity>BEGIN:VCARD
FN:Suilen, A.
N:Suilen\, A.
VERSION:3.0
END:VCARD</entity>
    <date>
      <dateTime>2007-01-01T08:32</dateTime>
    </date>
    <description>
      <string language="x-none">Dit gaat ergens over.</string>
    </description>
  </annotation>
  <classification>
    <purpose>
      <source>LOMv1.0</source>
      <value>discipline</value>
    </purpose>
    <taxonPath>
      <source/>
      <taxon>
        <id>
                                        00047
                                </id>
        <entry>
          <string language="x-none">NBC groeps NAAM</string>
        </entry>
      </taxon>
    </taxonPath>
    <description>
      <string language="x-none">Vakgebied</string>
    </description>
    <keyword>
      <string language="x-none">vakgebied discipline onderwerp</string>
    </keyword>
  </classification>
</lom>
"""
        tree = parse(StringIO(xml))
        from lxml.etree import XMLSchema
        schema = XMLSchema(parse(open('../meresco/components/xml_generic/schemas-lom/lomCcNbc.xsd')))
        validate = Validate()
        validate.unknown('msg', 'id', 'name', tree)
        schema.validate(tree)
        self.assertEquals(None, schema.error_log.last_error)

    def testOne(self):
        list(self.crosswalk.unknown('crosswalk', 'id', 'metadata', theXmlRecord=parse(readRecord('imsmd_v1p2-1.xml'))))
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEquals(2, len(self.observer.calledMethods[0].arguments))
        arguments = self.observer.calledMethods[0].arguments
        self.assertEquals("id", arguments[0])
        self.assertEquals("metadata", arguments[1])

    def testValidate(self):
        try:
            list(self.validate.unknown('methodname', 'id', 'metadata', parse(readRecord('lom-cc-nbc.xml'))))
        except Exception, e:
            self.fail(e)

        try:
            list(self.validate.unknown('methodname', 'id', 'metadata', parse(readRecord('imsmd_v1p2-1.xml'))))
            self.fail('must raise exception')
        except Exception, e:
            self.assertEquals("<string>:1:ERROR:SCHEMASV:SCHEMAV_CVC_ELT_1: Element '{http://dpc.uba.uva.nl/schema/lom/triplel}lom': No matching global declaration available for the validation root.", str(e))

    def testTripleLExample(self):
        try:
            self.crosswalk.unknown('methodname', 'id', 'metadata', theXmlRecord=parse(readRecord('triple-lrecord.xml')))
        except Exception, e:
            message = readRecord('triple-lrecord.xml').read()
            for n, line in enumerate(message.split('\n')):
                print n+1, line
            raise

    def testNormalize(self):
        list(self.crosswalk.unknown('add', None, 'metadata', theXmlRecord=parse(readRecord('triple-lrecord.xml'))))
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertFalse('2006-11-28 19:00' in tostring(self.observer.calledMethods[0].kwargs['theXmlRecord']))


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

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
from unittest import TestCase
from cq2utils import CallTrace

from meresco.core import Observable
from meresco.components import Xml2Fields

from lxml.etree import parse
from StringIO import StringIO

def parselxml(aString):
    return parse(StringIO(aString)).getroot()

class Xml2FieldsTest(TestCase):

    def setUp(self):
        xml2fields = Xml2Fields()
        self.observer = CallTrace('Observer')
        xml2fields.addObserver(self.observer)
        self.observable = Observable()
        self.observable.addObserver(xml2fields)

    def testOneField(self):
        self.observable.do.add('id0','partName', parselxml('<fields><tag>value</tag></fields>'))
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEquals("addField(name='fields.tag', value='value')", str(self.observer.calledMethods[0]))

    def testDoNotIncludeNamespaces(self):
        self.observable.do.add('id0','partName', parselxml('<fields xmlns="aap"><tag>value</tag></fields>'))
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEquals("addField(name='fields.tag', value='value')", str(self.observer.calledMethods[0]))

    def testMultiLevel(self):
        node = parselxml("""<lom>
            <general>
                <title>The title</title>
            </general>
        </lom>""")
        self.observable.do.add('id', 'legacy partname', node)
        self.assertEquals("addField(name='lom.general.title', value='The title')", str(self.observer.calledMethods[0]))

    def testMultipleValuesForField(self):

        node = parselxml("""<tag>
            <name>Name One</name>
            <name>Name Two</name>
        </tag>""")
        self.observable.do.add('id', 'legacy partname', node)
        self.assertEquals(2, len(self.observer.calledMethods))
        self.assertEquals("addField(name='tag.name', value='Name One')", str(self.observer.calledMethods[0]))
        self.assertEquals("addField(name='tag.name', value='Name Two')", str(self.observer.calledMethods[1]))

    def testIgnoreCommentsAndEmptyTags(self):
        node = parselxml("""<tag>
            <!-- comment line, ignore me -->
            <name>Name One</name>
            <name>Name Two</name>
            <name>
            </name>
        </tag>""")
        self.observable.do.add('id', 'legacy partname', node)
        self.assertEquals(2, len(self.observer.calledMethods))
        self.assertEquals("addField(name='tag.name', value='Name One')", str(self.observer.calledMethods[0]))
        self.assertEquals("addField(name='tag.name', value='Name Two')", str(self.observer.calledMethods[1]))

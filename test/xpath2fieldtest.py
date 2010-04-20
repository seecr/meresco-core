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
from cq2utils import CQ2TestCase, CallTrace

from meresco.components import XPath2Field

from lxml.etree import parse
from StringIO import StringIO

class XPath2FieldTest(CQ2TestCase):
    def testSingleXPath2Field(self):
        observer = CallTrace()
        xpath2field = XPath2Field([('/a/b//@attr', 'a.b.attr')], namespaceMap={'ns': 'http://namespace.org/'})
        xpath2field.addObserver(observer)

        node = parse(StringIO("""<a>
            <b attr="The Attribute">
               content of the b tag
            </b>
        </a>"""))

        xpath2field.add('id', 'partname', node)
        self.assertEquals(1, len(observer.calledMethods))

        self.assertEquals("addField(name='a.b.attr', value='The Attribute')", str(observer.calledMethods[0]))

    def testMultipleXPath2Field(self):
        observer = CallTrace()
        xpath2field = XPath2Field([('/a/b//@attr', 'a.b.attr')], namespaceMap={'ns': 'http://namespace.org/'})
        xpath2field.addObserver(observer)

        node = parse(StringIO("""<a>
            <b attr="attr_1">
               content of the b tag
            </b>
            <b attr="attr_2">
               content of the b tag
            </b>
            <b attr="attr_3">
               content of the b tag
            </b>
        </a>"""))

        xpath2field.add('id', 'partname', node)
        self.assertEquals(3, len(observer.calledMethods))
        self.assertEquals("addField(name='a.b.attr', value='attr_1')", str(observer.calledMethods[0]))
        self.assertEquals("addField(name='a.b.attr', value='attr_2')", str(observer.calledMethods[1]))
        self.assertEquals("addField(name='a.b.attr', value='attr_3')", str(observer.calledMethods[2]))

    def testSendAsList(self):
        observer = CallTrace()
        xpath2field = XPath2Field([('/a/b/text()', 'a.bees')], sendAsList=True)
        xpath2field.addObserver(observer)

        node = parse(StringIO("""<a><b>1</b><b>2</b><b>3</b><b>4</b></a>"""))

        xpath2field.add('id', 'partname', node)
        self.assertEquals(1, len(observer.calledMethods))
        self.assertEquals(['1','2','3','4'], observer.calledMethods[0].kwargs['value'])
        

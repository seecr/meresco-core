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

from cStringIO import StringIO
from cq2utils.cq2testcase import CQ2TestCase
from meresco.framework.observable import Observable
from cq2utils.component import Notification
from cq2utils.calltrace import CallTrace
from amara import binderytools
from lxml.etree import _ElementTree, tostring, parse

from meresco.components.xmlpump import XmlInflate, XmlDeflate, Amara2Lxml, Lxml2Amara

class XmlPumpTest(CQ2TestCase):

    def testInflate(self):
        observer = CallTrace('Observer')
        xmlInflate = XmlInflate()
        xmlInflate.addObserver(observer)

        xmlString = """<tag><content>contents</content></tag>"""
        list(xmlInflate.add("id", "partName", xmlString))

        self.assertEquals(1, len(observer.calledMethods))
        self.assertEquals("add", observer.calledMethods[0].name)
        self.assertEquals(["id", "partName"], observer.calledMethods[0].arguments[:2])

        xmlNode = observer.calledMethods[0].arguments[2]
        self.assertEquals('tag', xmlNode.localName)
        self.assertEquals('content', xmlNode.content.localName)

    def testDeflate(self):
        observer = CallTrace('Observer')
        xmlDeflate = XmlDeflate()
        xmlDeflate.addObserver(observer)

        s = """<tag><content>contents</content></tag>"""
        list(xmlDeflate.add("id", "partName", binderytools.bind_string(s).tag))

        self.assertEquals(1, len(observer.calledMethods))
        self.assertEquals("add", observer.calledMethods[0].name)
        self.assertEquals(["id", "partName", s], observer.calledMethods[0].arguments)

    def testAmara2LXml(self):
        class Observer:
            def ape(inner, lxmlNode):
                self.lxmlNode = lxmlNode
        amara2lxml = Amara2Lxml()
        amara2lxml.addObserver(Observer())
        amaraNode = binderytools.bind_string('<a><b>c</b></a>')
        list(amara2lxml.unknown('ape', amaraNode))
        self.assertEquals(_ElementTree, type(self.lxmlNode))
        self.assertEquals('<a><b>c</b></a>', tostring(self.lxmlNode))

    def testLxml2Amara(self):
        class Observer:
            def ape(inner, amaraNode):
                self.amaraNode = amaraNode
        lxml2amara = Lxml2Amara()
        lxml2amara.addObserver(Observer())
        lxmlNode = parse(StringIO('<a><b>c</b></a>'))
        list(lxml2amara.unknown('ape', lxmlNode))
        self.assertEquals("<class 'amara.bindery.root_base'>", str(type(self.amaraNode)))
        self.assertEquals('<?xml version="1.0" encoding="UTF-8"?>\n<a><b>c</b></a>', self.amaraNode.xml())

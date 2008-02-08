## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school.
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

from meresco.components.xml2document import TEDDY_NS
from meresco.components.dictionary import DocumentDict
from meresco.components.dictionary.documentdict import fromDict, asDict
from meresco.components import Accumulate
from amara.bindery import is_element, root_base
from amara.binderytools import bind_string, create_document
from meresco.framework import Observable

class AccumulateTest(TestCase):
    def createAmaraBasedAccumulate(self, rootTagName):
        def combine(argumentCollection):
            doc = create_document()
            rootTag = doc.xml_create_element(unicode(rootTagName))
            for args,kwargs in argumentCollection:
                assert len(args) == 3
                assert kwargs == {}
                identifier, partName, dataNode = args
                rootTag.xml_append(dataNode)
            return [identifier, rootTagName, rootTag], {}
        return Accumulate(message = "add", combine = combine)


    def testMessages(self):
        startingPoint = Observable()
        accumulate = self.createAmaraBasedAccumulate('tagName')
        observer = CallTrace("observer")
        startingPoint.addObserver(accumulate)
        accumulate.addObserver(observer)
        startingPoint.do.add('identifier', 'data', bind_string('<data>data</data>').data)
        startingPoint.do.finish()

        self.assertEquals(1, len(observer.calledMethods))
        method = observer.calledMethods[0]
        self.assertEquals("add", method.name)
        self.assertEquals(3, len(method.arguments))
        identifier, partName, xmlNode = method.arguments
        self.assertEquals("identifier", identifier)
        self.assertEquals("tagName", partName)
        self.assertTrue(is_element(xmlNode))
        self.assertFalse(root_base == type(xmlNode))
        self.assertEquals('<tagName><data>data</data></tagName>', xmlNode.xml())

    def testMultipleParts(self):
        accumulate = self.createAmaraBasedAccumulate('tag')
        observer = CallTrace("observer")
        accumulate.addObserver(observer)

        list(accumulate.unknown('add', 'identifier', 'data', bind_string('<data>data</data>').data))
        list(accumulate.unknown('add', 'identifier', 'other', bind_string('<other>data</other>').other))
        list(accumulate.finish())

        self.assertEquals(1, len(observer.calledMethods))
        method = observer.calledMethods[0]
        identifier, partName, xmlNode = method.arguments
        self.assertEquals('<tag><data>data</data><other>data</other></tag>', xmlNode.xml())

    def testNewIdentifierTriggersSendingOfPrevious(self):
        startingPoint = Observable()
        accumulate = self.createAmaraBasedAccumulate('tag')
        observer = CallTrace("observer")
        accumulate.addObserver(observer)
        startingPoint.addObserver(accumulate)

        startingPoint.do.add('one', 'other', bind_string('<other>data1</other>').other)
        startingPoint.do.add('one', 'data', bind_string('<data>data1</data>').data)
        startingPoint.do.add('two', 'data', bind_string('<data>data2</data>').data)
        self.assertEquals(1, len(observer.calledMethods))
        startingPoint.do.add('two', 'other', bind_string('<other>data2</other>').other)
        startingPoint.do.finish()
        self.assertEquals(2, len(observer.calledMethods))
        method1 = observer.calledMethods[0]
        method2 = observer.calledMethods[1]
        identifier, partName, xmlNode1 = method1.arguments
        identifier, partName, xmlNode2 = method2.arguments
        self.assertEquals('<tag><other>data1</other><data>data1</data></tag>', xmlNode1.xml())
        self.assertEquals('<tag><data>data2</data><other>data2</other></tag>', xmlNode2.xml())


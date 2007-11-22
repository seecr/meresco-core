from unittest import TestCase

from cq2utils import CallTrace

from meresco.components.xml2document import TEDDY_NS
from meresco.components.dictionary import DocumentDict
from meresco.components.dictionary.documentdict import fromDict, asDict
from meresco.components import Accumulate
from amara.binderytools import bind_string
from amara.bindery import is_element, root_base

class AccumulateTest(TestCase):
    def testMessages(self):
        accumulate = Accumulate('tagName')
        observer = CallTrace("observer")
        accumulate.addObserver(observer)
        accumulate.add('identifier', 'data', bind_string('<data>data</data>').data)
        accumulate.finish()

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
        accumulate = Accumulate('tag')
        observer = CallTrace("observer")
        accumulate.addObserver(observer)

        accumulate.add('identifier', 'data', bind_string('<data>data</data>').data)
        accumulate.add('identifier', 'other', bind_string('<other>data</other>').other)
        accumulate.finish()

        self.assertEquals(1, len(observer.calledMethods))
        method = observer.calledMethods[0]
        identifier, partName, xmlNode = method.arguments
        self.assertEquals('<tag><data>data</data><other>data</other></tag>', xmlNode.xml())

    def testNewIdentifierTriggersSendingOfPrevious(self):
        accumulate = Accumulate('tag')
        observer = CallTrace("observer")
        accumulate.addObserver(observer)

        accumulate.add('one', 'other', bind_string('<other>data1</other>').other)
        accumulate.add('one', 'data', bind_string('<data>data1</data>').data)
        accumulate.add('two', 'data', bind_string('<data>data2</data>').data)
        self.assertEquals(1, len(observer.calledMethods))
        accumulate.add('two', 'other', bind_string('<other>data2</other>').other)
        accumulate.finish()
        self.assertEquals(2, len(observer.calledMethods))
        method1 = observer.calledMethods[0]
        method2 = observer.calledMethods[1]
        identifier, partName, xmlNode1 = method1.arguments
        identifier, partName, xmlNode2 = method2.arguments
        self.assertEquals('<tag><other>data1</other><data>data1</data></tag>', xmlNode1.xml())
        self.assertEquals('<tag><data>data2</data><other>data2</other></tag>', xmlNode2.xml())


    def testIllegalArguments(self):
        accumulate = Accumulate('tag')
        observer = CallTrace("observer")
        accumulate.addObserver(observer)

        try:
            accumulate.add('identifier', 'data', bind_string('<amara>root_base</amara>'))
            self.fail()
        except AssertionError, e:
            self.assertEquals('Expects amara elements, not amara documents.', str(e))

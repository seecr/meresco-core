
from cq2utils import CQ2TestCase as TestCase

from meresco.framework import Observable
from StringIO import StringIO

from meresco.components import XmlCompose

class XmlComposeTest(TestCase):
    def testOne(self):
        observable = Observable()
        xmlcompose = XmlCompose(
            template = """<template><one>%(one)s</one><two>%(two)s</two></template>""",
            nsMap = {'ns1': "http://namespaces.org/ns1"},
            one = ('partname1', '/ns1:one/ns1:tag/text()'),
            two = ('partname2', '/two/tag/@name')
        )
        observable.addObserver(xmlcompose)
        observer = MockStorage()
        xmlcompose.addObserver(observer)

        result = ''.join(list(observable.any.getRecord("recordId")))
        self.assertEqualsWS(result, """<template><one>1</one><two>&lt;one&gt;</two></template>""")

    def testModuloThing(self):
        class SubXmlCompose(XmlCompose):
            def createRecord(self, aDictionary):
                return '|'.join([
                    aDictionary['one'],
                    aDictionary['two'].upper(),
                    aDictionary['three'].swapcase()
                ])
        observable = Observable()
        xmlcompose = SubXmlCompose(
            template = None,
            nsMap = {},
            one = ('partname3', '/root/one/text()'),
            two = ('partname3', '/root/two/text()'),
            three = ('partname3', '/root/three/text()'),
        )
        observable.addObserver(xmlcompose)
        observer = MockStorage()
        xmlcompose.addObserver(observer)

        result = ''.join(list(observable.any.getRecord("recordId")))
        self.assertEqualsWS(result, """One|TWO|thrEE""")

    
class MockStorage(object):
    def __init__(self):
        self.timesCalled = 0

    def getStream(self, ident, partname):
        self.timesCalled += 1
        if partname == 'partname1':
            return StringIO("""<one xmlns="http://namespaces.org/ns1"><tag>1</tag><tag>2</tag><escaped>&amp;</escaped></one>""")
        elif partname == 'partname2':
            return StringIO("""<two><tag name="&lt;one&gt;">one</tag><tag name="&quot;two'">two</tag></two>""")
        elif partname == 'partname3':
            return StringIO("""<root><one>One</one><two>TWo</two><three>THRee</three></root>""")
        

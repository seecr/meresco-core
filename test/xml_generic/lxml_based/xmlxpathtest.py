
from cq2utils import CQ2TestCase, CallTrace
from cq2utils.xmlutils import findNamespaces
from meresco.framework import Observable

from meresco.components import XmlXPath, XmlParseLxml, XmlPrintLxml
from lxml.etree import parse, ElementTree, _ElementTree as ElementTreeType, tostring
from StringIO import StringIO


class XmlXPathTest(CQ2TestCase):
        
    def createXmlXPath(self, xpathList, nsMap):
        self.observable = Observable()
        self.observer = CallTrace('observer')
        self.observable.addObservers([
            (XmlParseLxml(), [
                (XmlXPath(xpathList, nsMap), [
                    (XmlPrintLxml(), [
                        self.observer
                    ])
                ])
            ])
        ])
    def testSimpleXPath(self):
        self.createXmlXPath(['/root/path'], {})

        self.observable.do.test('een tekst', '<root><path><to>me</to></path></root>')

        self.assertEquals(1, len(self.observer.calledMethods))
        method = self.observer.calledMethods[0]
        self.assertEquals('test', method.name)
        self.assertEquals(2, len(method.args))
        self.assertEquals('een tekst', method.args[0])
        self.assertEqualsWS('<path><to>me</to></path>', method.args[1])
        
    def testElementInKwargs(self):
        self.createXmlXPath(['/root/path'], {})
        
        self.observable.do.aMethod('otherArgument', aKeyword='<root><path><to>me</to></path></root>', otherKeyword='okay')
        
        self.assertEquals(1, len(self.observer.calledMethods))
        method = self.observer.calledMethods[0]
        self.assertEquals('aMethod', method.name)
        self.assertEquals(1, len(method.args))
        self.assertEquals(set(['aKeyword', 'otherKeyword']), set(method.kwargs.keys()))
        self.assertEqualsWS('<path><to>me</to></path>', method.kwargs['aKeyword'])
        
    def testNoElementInArgumentsPassesOn(self):
        self.createXmlXPath(['/root/path'], {})
        
        self.observable.do.aMethod('do not xpath me') 
    
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEquals('do not xpath me', self.observer.calledMethods[0].args[0])

    def testXPathWithNamespaces(self):
        self.createXmlXPath(['/a:root/b:path/c:findme'], {'a':'ns1', 'b':'ns2', 'c':'ns3'})
        
        self.observable.do.aMethod("""<root xmlns="ns1" xmlns:two="ns2">
            <two:path><findme xmlns="ns3">Found</findme></two:path></root>""") 
    
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEqualsWS('<findme xmlns="ns3">Found</findme>', self.observer.calledMethods[0].args[0])

       
    def testXPathWithConditions(self):
        self.createXmlXPath(['/root/element[pick="me"]/data'], {})
        
        self.observable.do.aMethod("""<root>
    <element>
        <pick>not me</pick>
        <data>Not this data</data>
    </element>
    <element>
        <pick>me</pick>
        <data>This data</data>
    </element>
</root>""") 
    
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEqualsWS('<data>This data</data>', self.observer.calledMethods[0].args[0])
        
    def testXPathWithMultipleResults(self):
        self.createXmlXPath(['/root/element/data'], {})
        
        self.observable.do.aMethod("""<root>
    <element>
        <data>one</data>
    </element>
    <element>
        <data>two</data>
    </element>
</root>""") 
        self.assertEquals(2, len(self.observer.calledMethods))
        self.assertEqualsWS('<data>one</data>', self.observer.calledMethods[0].args[0])
        self.assertEqualsWS('<data>two</data>', self.observer.calledMethods[1].args[0])
            
    def testXPathWithNoResults(self):
        self.createXmlXPath(['/does/not/exist'], {})
        
        self.observable.do.aMethod("""<some><element>data</element></some>""") 
        self.assertEquals(0, len(self.observer.calledMethods))
        
    def testOnlyOneXMLAllowed(self):
        self.createXmlXPath('/root', {})
        try:
            self.observable.do.aMethod("<somexml/>", xml="<otherxml/>")
            self.fail()
        except AssertionError, e:
            self.assertEquals('Can only handle one ElementTree in argument list.', str(e))
            
    def testDoNotChangesArgs(self):
        xmlXPath = XmlXPath(['/a'])
        arg = parse(StringIO('<a>a</a>'))
        xmlXPath.unknown('message', arg)
        self.assertEquals('<a>a</a>', tostring(arg))

    def testNamespaces(self):
        xmlXPath = XmlXPath(['/a:aNode/b:bNode'], {'a':'aNamespace', 'b':'bNamespace' })
        arg = parse(StringIO('<aNode xmlns="aNamespace"><bNode xmlns="bNamespace">ccc</bNode></aNode>'))
        observer = CallTrace('Observer')
        observable = Observable()
        observable.addObserver(xmlXPath)
        xmlXPath.addObserver(observer)
        
        observable.do.message(arg)

        message = observer.calledMethods[0]
        self.assertEquals('message', message.name)
        newNode = message.args[0]
        self.assertEqualsWS('<bNode xmlns="bNamespace">ccc</bNode>', tostring(newNode))
        
        newNamespaces = findNamespaces(newNode)
        nameSpacesAfterParsing = findNamespaces(parse(StringIO(tostring(newNode))))
        self.assertEquals(nameSpacesAfterParsing, newNamespaces)

    def testFindUsingMultipleXPaths(self):
        self.createXmlXPath(['/does/not/exist', '/a/b', '/a/b/c'], {})

        self.observable.do.test('<a><b><c>one</c></b><b><d>two</d></b></a>')

        self.assertEquals(3, len(self.observer.calledMethods))
        allResults = []
        for method in self.observer.calledMethods:
            allResults.append(method.args[0])
        self.assertEqualsWS('<b><c>one</c></b>', allResults[0])
        self.assertEqualsWS('<b><d>two</d></b>', allResults[1])
        self.assertEqualsWS('<c>one</c>', allResults[2])
        
    def testTestWithCondition(self):
        self.createXmlXPath(['/a/*[not(self::b) and not(self::c)]'], {})

        self.observable.do.test('<a><b>zero</b><c>one</c><d>two</d></a>')

        self.assertEquals(1, len(self.observer.calledMethods))
        allResults = []
        for method in self.observer.calledMethods:
            allResults.append(method.args[0])
        self.assertEqualsWS('<d>two</d>', allResults[0])
    
    def testTestWithConditionAndNS(self):
        self.createXmlXPath(['/a:a/*[not(self::a:b) and not(self::a:c)]'], {"a":"aSpace"})

        self.observable.do.test('<z:a xmlns:z="aSpace"><z:b>zero</z:b><z:c>one</z:c><z:d>two</z:d></z:a>')

        self.assertEquals(1, len(self.observer.calledMethods))
        allResults = []
        for method in self.observer.calledMethods:
            allResults.append(method.args[0])
        self.assertEqualsWS('<d>two</d>', allResults[0])

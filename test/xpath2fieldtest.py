from cq2utils import CQ2TestCase, CallTrace

from meresco.components import XPath2Field

from lxml.etree import parse
from StringIO import StringIO

class XPath2FieldTest(CQ2TestCase):
   def testSingleXPath2Field(self):
        observer = CallTrace()
        xml2dict = XPath2Field([('/a/b//@attr', 'a.b.attr')], namespaceMap={'ns': 'http://namespace.org/'})
        xml2dict.addObserver(observer)

        node = parse(StringIO("""<a>
            <b attr="The Attribute">
               content of the b tag
            </b>
        </a>"""))

        list(xml2dict.add('id', 'partname', node))
        self.assertEquals(2, len(observer.calledMethods))
        addFieldMethod = observer.calledMethods[0]
        self.assertEquals('add', observer.calledMethods[1].name)
        self.assertEquals('addField', addFieldMethod.name)
        self.assertEquals('a.b.attr', addFieldMethod.kwargs['name'])
        self.assertEquals(['The Attribute'], addFieldMethod.kwargs['value'])
        
   def testMultipleXPath2Field(self):
        observer = CallTrace()
        xml2dict = XPath2Field([('/a/b//@attr', 'a.b.attr')], namespaceMap={'ns': 'http://namespace.org/'})
        xml2dict.addObserver(observer)

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

        list(xml2dict.add('id', 'partname', node))
        self.assertEquals(2, len(observer.calledMethods))
        addFieldMethod = observer.calledMethods[0]
        self.assertEquals('addField', addFieldMethod.name)
        self.assertEquals('a.b.attr', addFieldMethod.kwargs['name'])
        self.assertEquals(['attr_1', 'attr_2', 'attr_3'], addFieldMethod.kwargs['value'])

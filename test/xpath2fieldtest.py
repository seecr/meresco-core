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

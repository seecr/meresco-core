from cq2utils import CQ2TestCase, CallTrace

from meresco.components.dictionary import XPath2Dict

from lxml.etree import parse
from StringIO import StringIO

class XPath2DictTest(CQ2TestCase):
   def testXPath2Dict(self):
        observer = CallTrace()
        xml2dict = XPath2Dict([('/a/b//@attr', 'a.b.attr')], namespaceMap={'ns': 'http://namespace.org/'})
        xml2dict.addObserver(observer)

        node = parse(StringIO("""<a>
            <b attr="The Attribute">
               content of the b tag
            </b>
        </a>"""))

        list(xml2dict.add('id', 'partname', node))
        documentDict = observer.calledMethods[0].args[1]
        self.assertEquals('The Attribute', documentDict.get('a.b.attr')[0].value)
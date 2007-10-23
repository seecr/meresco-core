from unittest import TestCase
from cq2utils.calltrace import CallTrace

from meresco.framework.observable import Observable

from meresco.components.dictionary import Xml2Dict, DocumentDict

from amara import binderytools

class Xml2DictTest(TestCase):
    def testOneField(self):
        xml2Dict = Xml2Dict()
        observer = CallTrace('Observer')
        xml2Dict.addObserver(observer)
        observable = Observable()
        observable.addObserver(xml2Dict)

        observable.do.add('id','partName', binderytools.bind_string('<fields><tag>value</tag></fields>').fields)

        self.assertEquals('addDocumentDict', observer.calledMethods[0].name)
        self.assertEquals(('id', 'partName'), observer.calledMethods[0].args[:2])
        documentDict = observer.calledMethods[0].args[2]
        self.assertEquals(1, len(documentDict.get('fields.tag')))
        self.assertEquals('value', documentDict.get('fields.tag')[0].value)


    def testMultiLevel(self):
        documentDict = DocumentDict()
        xml2dict = Xml2Dict()

        node = binderytools.bind_string("""<lom>
            <general>
                <title>The title</title>
            </general>
        </lom>""").lom
        xml2dict._fillDict(node, documentDict, '')
        self.assertEquals('The title', documentDict.get('lom.general.title')[0].value)

    def testMultipleValuesForField(self):
        documentDict = DocumentDict()
        xml2dict = Xml2Dict()

        node = binderytools.bind_string("""<tag>
            <name>Name One</name>
            <name>Name Two</name>
        </tag>""").tag
        xml2dict._fillDict(node, documentDict, '')
        self.assertEquals(['Name One', 'Name Two'], [field.value for field in documentDict.get('tag.name')])

from amara import binderytools
from amara.bindery import is_element
from meresco.framework.observable import Observable
from meresco.components.dictionary import DocumentDict

class Xml2Dict(Observable):

    def add(self, id, partName, amaraXmlNode):
        dd = DocumentDict()
        self._fillDict(amaraXmlNode, dd, '')
        return self.all.addDocumentDict(id, partName, dd)

    def _fillDict(self, aNode, dd, parentName):
        if parentName:
            parentName += '.'
        tagname = parentName + str(aNode.localName)
        value = aNode.xml_child_text
        if str(value).strip():
            dd.add(tagname, str(value))

        for child in filter(is_element, aNode.childNodes):
            self._fillDict(child, dd, tagname)

    def unknown(self, *args, **kwargs):
        return self.all.unknown(*args, ** kwargs)
        

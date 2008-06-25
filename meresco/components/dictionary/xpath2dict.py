
from meresco.framework import Observable
from documentdict import DocumentDict

class XPath2Dict(Observable):
    def __init__(self, attributeXpaths=[], namespaceMap={}):
        Observable.__init__(self)
        self._attributeXpaths = attributeXpaths
        self._namespaceMap = namespaceMap

    def add(self, id, partName, lxmlNode):
        dd = DocumentDict()
        for (xpath, dottedDestinationPath) in self._attributeXpaths:
            attribute = lxmlNode.xpath(xpath, namespaces=self._namespaceMap)
            if attribute:
                dd.add(dottedDestinationPath, attribute[0])
        return self.all.addDocumentDict(id, dd)
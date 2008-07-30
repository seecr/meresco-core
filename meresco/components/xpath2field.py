from meresco.framework import Observable


class XPath2Field(Observable):
    def __init__(self, attributeXpaths=[], namespaceMap={}):
        Observable.__init__(self)
        self._attributeXpaths = attributeXpaths
        self._namespaceMap = namespaceMap

    def add(self, id, partName, lxmlNode):
        for (xpath, dottedDestinationPath) in self._attributeXpaths:
            values = lxmlNode.xpath(xpath, namespaces=self._namespaceMap)
            for value in values:
                self.do.addField(name=dottedDestinationPath, value=value)

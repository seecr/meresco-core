
from meresco.framework import Observable
from lxml.etree import ElementTree, _ElementTree as ElementTreeType

oftenUsedNamespaces = {
    'oai_dc': "http://www.openarchives.org/OAI/2.0/oai_dc/",
    'dc': "http://purl.org/dc/elements/1.1/",
    'oai': "http://www.openarchives.org/OAI/2.0/",
    'lom': "http://ltsc.ieee.org/xsd/LOM",
}

class XmlXPath(Observable):
    def __init__(self, xpath, namespaceMap = {}):
        Observable.__init__(self)
        self._xpath = xpath
        self._namespacesMap = oftenUsedNamespaces.copy()
        self._namespacesMap.update(namespaceMap)

    def unknown(self, msg, *args, **kwargs):
        changeTheseArgs = [(position,arg) for position,arg in enumerate(args) if type(arg) == ElementTreeType]
        changeTheseKwargs = [(key,value) for key,value in kwargs.items() if type(value) == ElementTreeType]
        assert len(changeTheseArgs) + len(changeTheseKwargs) <= 1, 'Can only handle one ElementTree in argument list.'

        if changeTheseArgs:
            position, elementTree = changeTheseArgs[0]
            for element in elementTree.xpath(self._xpath, self._namespacesMap):
                newTree = ElementTree(element)
                newArgs = [arg for arg in args]
                newArgs[position] = newTree
                yield self.all.unknown(msg, *newArgs, **kwargs)
        elif changeTheseKwargs:
            key, elementTree = changeTheseKwargs[0]
            for element in elementTree.xpath(self._xpath, self._namespacesMap):
                newTree = ElementTree(element)
                newKwargs = kwargs.copy()
                newKwargs[key] = newTree
                yield self.all.unknown(msg, *args, **newKwargs)
        else:
            yield self.all.unknown(msg, *args, **kwargs)


from meresco.framework import Observable
from lxml.etree import ElementTree, _ElementTree as ElementTreeType

class XmlXPath(Observable):
    def __init__(self, xpath, namespaceMap = {}):
        Observable.__init__(self)
        self._xpath = xpath
        self._namespacesMap = namespaceMap

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

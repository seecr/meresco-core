
from meresco.framework.observable import Observable

from amara.bindery import is_element
import re

class CleanSplit:

    def __init__(self, separator):
        self.separator = separator

    def __call__(self, s):
        return [part.strip() for part in s.split(self.separator)]

def years(s):
    yearRe = re.compile('\d{4}')
    return yearRe.findall(s)


class FieldSplit(Observable):
    def __init__(self, fieldname, splitter):
        Observable.__init__(self)
        self.fieldname = fieldname
        self.splitter = splitter

    def add(self, id, partName, amaraXmlNode):
        nodes = self._findNodes(amaraXmlNode, self.fieldname)
        for node in nodes:
            content = unicode(node)
            parentNode = node.parentNode
            parts = self.splitter(content)
            for part in parts:
                newElement = amaraXmlNode.xml_create_element(node.nodeName,
                    ns=node.namespaceURI, content=part)
                parentNode.xml_append(newElement)
            parentNode.xml_remove_child(node)
        self.do.add(id, partName, amaraXmlNode)

    def _findNodes(self, node, nodeName):
        chunks = nodeName.split('.')
        localName = chunks[0]
        if node.localName != localName:
            return []
        if len(chunks) == 1:
            return [node]
        else:
            result = []
            remainder = '.'.join(chunks[1:])
            if remainder:
                for child in filter(lambda x:is_element(x), node.childNodes):
                    result += self._findNodes(child, remainder)
            return result
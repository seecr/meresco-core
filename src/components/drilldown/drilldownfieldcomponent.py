from meresco.framework.observable import Observable
from meresco.components.xml2document import TEDDY_NS

class DrilldownFieldComponent(Observable):
    def __init__(self, listOfFields):
        Observable.__init__(self)
        self._drilldownFields = listOfFields

    def add(self, id, partName, amaraXmlNode):
        for field in self._drilldownFields:
            nodes = amaraXmlNode.xml_xpath("//%s" % field)
            if nodes:
                node = nodes[0]
                newfield = amaraXmlNode.xml_create_element('%s__untokenized__' % node.nodeName,
                    content=unicode(node),
                    attributes={(u'teddy:tokenize', unicode(TEDDY_NS)): u'false'})
                amaraXmlNode.xml_append(newfield)
        return self.all.add(id, partName, amaraXmlNode)

    def unknown(self, message, *args, **kwargs):
        return self.all.unknown(message, *args, **kwargs)

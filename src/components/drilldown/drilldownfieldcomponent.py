from cq2utils.component import Component
from meresco.framework.observable import Observable

from meresco.components.xml2document import TEDDY_NS

class DrilldownFieldComponent(Component, Observable):
    def __init__(self, listOfFields):
        Observable.__init__(self)
        self._drilldownFields = listOfFields

    def add(self, aNotification):
        xml = aNotification.payload
        for field in self._drilldownFields:
            nodes = xml.xml_xpath("//%s" % field)
            if nodes:
                node = nodes[0]
                newfield = xml.xml_create_element('%s__untokenized__' % node.nodeName,
                    content=unicode(node),
                    attributes={(u'teddy:tokenize', unicode(TEDDY_NS)): u'true'})
                xml.xml_append(newfield)
        self.changed(aNotification)
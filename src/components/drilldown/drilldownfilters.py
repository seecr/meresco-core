from meresco.framework.observable import Observable
from meresco.components.xml2document import TEDDY_NS

TOKEN = '__untokenized__'

class DrillDownRequestFieldFilter(Observable):
    def __init__(self, listOfFields):
        Observable.__init__(self)
        self._fields = listOfFields

    def drillDown(self, docNumbers, fieldsAndMaximums):
        translatedFields = ((s + TOKEN, i) 
            for (s, i) in fieldsAndMaximums 
            if s in self._fields)
        drillDownResults = self.any.drillDown(docNumbers, translatedFields)
        return ((field[:-len(TOKEN)], termCounts) 
            for field, termCounts in drillDownResults 
            if field[:-len(TOKEN)] in self._fields)


class DrillDownUpdateFieldFilter(Observable):
    def __init__(self, listOfFields):
        Observable.__init__(self)
        self._drilldownFields = listOfFields

    def add(self, id, partName, amaraXmlNode):
        for field in self._drilldownFields:
            nodes = amaraXmlNode.xml_xpath("//%s" % field)
            if nodes:
                node = nodes[0]
                newfield = amaraXmlNode.xml_create_element(node.nodeName + TOKEN,
                    content=unicode(node),
                    attributes={(u'teddy:tokenize', unicode(TEDDY_NS)): u'false'})
                amaraXmlNode.xml_append(newfield)
        return self.all.add(id, partName, amaraXmlNode)

    def unknown(self, message, *args, **kwargs):
        return self.all.unknown(message, *args, **kwargs)

from meresco.framework.observable import Observable
from meresco.components.xml2document import TEDDY_NS

TOKEN = '__untokenized__'

class DrillDownRequestFieldnameMap(Observable):
    def __init__(self, lookup, reverse):
        Observable.__init__(self)
        self.lookup = lookup
        self.reverse = reverse

    def drillDown(self, docNumbers, fieldsAndMaximums):
        translatedFields = ((self.lookup(field), maximum) 
            for (field, maximum) in fieldsAndMaximums)
        drillDownResults = self.any.drillDown(docNumbers, translatedFields)
        return ((self.reverse(field), termCounts) 
            for field, termCounts in drillDownResults)

class DrillDownRequestFieldFilter(DrillDownRequestFieldnameMap):
    def __init__(self):
        DrillDownRequestFieldnameMap.__init__(self,
            lambda field: field + TOKEN,
            lambda field: field[:-len(TOKEN)])
                
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
        self.do.add(id, partName, amaraXmlNode)

    def unknown(self, message, *args, **kwargs):
        self.do.unknown(message, *args, **kwargs)

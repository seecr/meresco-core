
from meresco.framework import Observable
from lxml.etree import parse
from xml.sax.saxutils import escape as xmlEscape

class XmlCompose(Observable):
    def __init__(self, template, nsMap, **fieldMapping):
        Observable.__init__(self)
        self._template = template
        self._nsMap = nsMap
        self._fieldMapping = fieldMapping
    
    def getRecord(self, aRecordId):
        data = {}
        cachedRecord = {}
        for tagName, values in self._fieldMapping.items():
            partname, xPathExpression = values
            if not partname in cachedRecord:
                cachedRecord[partname] = self._getPart(aRecordId, partname)
            xml = cachedRecord[partname]
            result = xml.xpath(xPathExpression, self._nsMap)
            if result:
                data[tagName] = str(result[0])
        yield self.createRecord(data)

    def createRecord(self, data):
        if len(data) != len(self._fieldMapping):
            raise StopIteration
        return self._template % dict(((k, xmlEscape(v)) for k,v in data.items()))

    def _getPart(self, recordId, partname):
        return parse(self.any.getStream(recordId, partname))
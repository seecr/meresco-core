from meresco.components.dictionary import DocumentDict
from meresco.framework import Observable

class DictAggregator(Observable):

    def addDocumentDict(self, id, partName, documentDict):
        aggregatedDict = DocumentDict()
        for originalField in documentDict:
            for aggregatedField in self.all.fieldsForField(originalField):
                aggregatedDict.addField(aggregatedField)
        #self.all.fieldsForDict(aggregatedDict) - ??? aggregatie naar zichzelf?
        
        self.do.addDocumentDict(id, partName, aggregatedDict)

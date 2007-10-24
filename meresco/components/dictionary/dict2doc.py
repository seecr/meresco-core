from meresco.components.lucene.document import Document as LuceneDocument
from meresco.framework import Observable

class Dict2Doc(Observable):
    
    def addDocumentDict(self, id, partName, documentDict):
        luceneDocument = LuceneDocument(id)
        for documentField in documentDict:
            luceneDocument.addIndexedField(documentField.key, documentField.value, documentField.options.get('tokenize', True))
        return self.all.add(id, partName, luceneDocument)

    def unknown(self, *args, **kwargs):
        return self.all.unknown(*args, ** kwargs)
from meresco.framework import Observable

from meresco.components.lucene import Document

class Fields2LuceneDocument(Observable):

    def __init__(self, tokenized=[]):
        Observable.__init__(self)
        self._tokenized = tokenized

    def addField(self, key, value):
        self.tx.values[key] = value

    def commit(self):
        document = Document(self.tx.values['__id__'])
        del self.tx.values['__id__']
        for key, value in self.tx.values.items():
            document.addIndexedField(key, value, key in self._tokenized)
        yield self.all.addDocument(document)
from meresco.framework import Observable
from meresco.components.lucene import Document

class Fields2LuceneDocument(Observable):

    def __init__(self, untokenized=[]):
        Observable.__init__(self)
        self._untokenized = untokenized
        self.txs = {}

    def begin(self):
        self.txs[self.tx.getId()] = Fields2LuceneDocumentTx(self, self._untokenized)

    def addField(self, key, value):
        self.txs[self.tx.getId()].addField(key, value)

    def commit(self):
        self.txs[self.tx.getId()].finalize()
        del self.txs[self.tx.getId()]


class Fields2LuceneDocumentTx(object):

    def __init__(self, parent, untokenized):
        self.parent = parent
        self.fields = {}
        self._untokenized = untokenized

    def addField(self, key, value):
        if not key in self.fields:
            self.fields[key] = []
        self.fields[key].append(value)

    def finalize(self):
        document = Document(self.fields['__id__'][0])
        del self.fields['__id__']
        for key, values in self.fields.items():
            for value in values:
                document.addIndexedField(key, value, not key in self._untokenized)
        self.parent.do.addDocument(document)



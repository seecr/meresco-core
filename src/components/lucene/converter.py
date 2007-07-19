import PyLucene

class Converter(object):
    def __init__(self, aLuceneIndexReader, fieldNames):
        self._reader = aLuceneIndexReader
        self._fieldNames = fieldNames

    def getDocSets(self):
        docSets = []
        for fieldName in self._fieldNames:
            docSets.append((fieldName, self._docSetsForFieldLucene(fieldName)))
        return docSets

    def docCount(self):
        return self._reader.numDocs()

    def _docSetsForFieldLucene(self, fieldName):
        result = []
        termDocs = self._reader.termDocs()
        termEnum = self._reader.terms(PyLucene.Term(fieldName, ''))
        #IndexReader.terms returns something of the following form, if fieldname == fieldname3
        #fieldname3 'abla'
        #fieldname3 'bb'
        #fielname3 'zz'
        #fieldname4 'aa'

        #The enum has the following (weird) behaviour: the internal pointer references
        #the first element by default, but when there are no elements it references a
        #None element. Therefor we have to check "if not term".
        #We use a "do ... while" idiom because calling next would advance the internal
        #pointer, resulting in a missed first element

        while True:
            term = termEnum.term()
            if not term or term.field() != fieldName:
                break
            termDocs.seek(term)

            docs = []
            while termDocs.next():
                docs.append(termDocs.doc())

            result.append((term.text(), docs))
            if not termEnum.next():
                break

        return result


from unittest import TestCase
from tempfile import gettempdir
from shutil import rmtree
from os.path import join

from meresco.components.lucene.converter import Converter
from meresco.components.lucene.lucene import LuceneIndex
from meresco.components.lucene.document import Document

#Helper functions:
def addUntokenized(index, documents):
    for docId, fields in documents:
        myDocument = Document(docId)
        for field, value in fields.items():
            myDocument.addIndexedField(field, value, tokenize = False)
        index.addToIndex(myDocument)
        index.reOpen()

class ConverterTest(TestCase):
    def setUp(self):
        self._tempdir = gettempdir() + '/testing'
        self._directoryName = join(self._tempdir, 'lucene-index')
        self._luceneIndex = LuceneIndex(self._directoryName)

    def tearDown(self):
        self._luceneIndex = None
        rmtree(self._tempdir)

    def testCreateDocSetsFromReader(self):
        addUntokenized(self._luceneIndex, [
            ('1', {'field_0': 'this is term_0', 'field_1': 'inquery'}),
            ('2', {'field_0': 'this is term_0', 'field_1': 'inquery'}),
            ('3', {'field_0': 'this is term_1', 'field_1': 'inquery'}),
            ('4', {'field_0': 'this is term_2', 'field_1': 'cannotbefound'})])

        converter = Converter(self._luceneIndex._getReader(), ['field_0', 'field_1'])
        docsets = list(converter.getDocSets())
        self.assertEquals(2, len(docsets))
        self.assertEquals([('field_0', [(u'this is term_0', [0, 1]), (u'this is term_1', [2]), (u'this is term_2', [3])]), ('field_1', [(u'cannotbefound', [3]), (u'inquery', [0, 1, 2])])], docsets)

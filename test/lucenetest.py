# -*- encoding: utf-8 -*-
## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) 2007 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2007 Stichting Kennisnet Ict op school. 
#       http://www.kennisnetictopschool.nl
#
#    This file is part of Meresco Core.
#
#    Meresco Core is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Meresco Core is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Meresco Core; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
#
# Lucene Test
#

import unittest
from tempfile import mkdtemp, gettempdir
import os
from shutil import rmtree
import PyLucene
from meresco.components.lucene.document import Document

from meresco.components.lucene.lucene import LuceneIndex
from meresco.components.lucene.document import IDFIELD

from PyLucene import Document as PyDocument, Field, IndexReader, IndexWriter, StandardAnalyzer, Term

class LuceneTest(unittest.TestCase):

    def _removeWhiteSpace(self, aString):
        return ''.join(aString.split())

    def assertEqualsWS(self, s1, s2):
        self.assertEquals(self._removeWhiteSpace(s1), self._removeWhiteSpace(s2))

    def setUp(self):
        self._tempdir = gettempdir()+'/testing'
        self.directoryName = os.path.join(self._tempdir, 'lucene-index')
        self._luceneIndex = LuceneIndex(self.directoryName)

    def tearDown(self):
        del self._luceneIndex
        if os.path.exists(self._tempdir):
            rmtree(self._tempdir)

    def testCreation(self):
        self.assertEquals(os.path.isdir(self.directoryName), True)
        self.assertTrue(IndexReader.indexExists(self.directoryName))

    def testAddToIndexWithDuplicateField(self):
        myDocument = Document('id')
        myDocument.addIndexedField('title', 'een titel')
        myDocument.addIndexedField('title', 'een sub titel')
        self._luceneIndex.addToIndex(myDocument)

        query = PyLucene.QueryParser('title', PyLucene.StandardAnalyzer()).parse('titel')
        hits = self._luceneIndex.query(query)
        self.assertEquals(len(hits), 1)

        query = PyLucene.QueryParser('title', PyLucene.StandardAnalyzer()).parse('sub')
        hits = self._luceneIndex.query(query)
        self.assertEquals(len(hits), 1)


    def testAddToIndex(self):
        myDocument = Document('0123456789')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addToIndex(myDocument)

        query = PyLucene.QueryParser('title', PyLucene.StandardAnalyzer()).parse('titel')
        hits = self._luceneIndex.query(query)
        self.assertEquals(len(hits), 1)
        hit = hits[0]
        i = 0
        for x in hit.fields():
            self.assertEquals(IDFIELD, x.name())
            i = i + 1
        self.assertEquals(1, i)
        self.assertEquals(hit.getField(IDFIELD).stringValue(), '0123456789')

    def testAddTwoDocuments(self):
        myDocument = Document('1')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addToIndex(myDocument)

        myDocument = Document('2')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addToIndex(myDocument)

        query = PyLucene.QueryParser('title', PyLucene.StandardAnalyzer()).parse('titel')
        hits = self._luceneIndex.query(query)
        self.assertEquals(2, len(hits))

    def testAddDocumentWithTwoValuesForOneField(self):
        myDocument = Document('1')
        myDocument.addIndexedField('field1', 'value_1')
        myDocument.addIndexedField('field1', 'value_2')
        self._luceneIndex.addToIndex(myDocument)

        def check(value):
            query = PyLucene.QueryParser('field1', PyLucene.StandardAnalyzer()).parse(value)
            hits = self._luceneIndex.query(query)
            self.assertEquals(1, len(hits))
        check('value_1')
        check('value_2')

    def testAddUTF8Document(self):
        myDocument = Document('0123456789')
        myDocument.addIndexedField('title', 'BijenkorfÂ´s')
        self._luceneIndex.addToIndex(myDocument)

    def testDeleteFromIndex(self):
        myDocument = Document('1')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addToIndex(myDocument)

        myDocument = Document('2')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addToIndex(myDocument)
        query = PyLucene.QueryParser('title', PyLucene.StandardAnalyzer()).parse('titel')
        hits = self._luceneIndex.query(query)
        self.assertEquals(2, len(hits))

        self._luceneIndex.deleteID('1')
        query = PyLucene.QueryParser('title', PyLucene.StandardAnalyzer()).parse('titel')
        hits = self._luceneIndex.query(query)
        self.assertEquals(1, len(hits))

    def testIndexCloses(self):
        myDocument = Document('1')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addToIndex(myDocument)
        self._luceneIndex = None
        newIndex = LuceneIndex(self.directoryName)
        newIndex.addToIndex(myDocument)

    def testDeletionDoesNotRaiseErrors(self):
        myDocument = Document('1')
        myDocument.addIndexedField('title', 'een titel')
        newIndex = LuceneIndex(self.directoryName+'2')
        newIndex.addToIndex(myDocument)
        rmtree(self.directoryName+'2')
        newIndex.__del__()

    def testCountField(self):
        self.assertEquals([], self._luceneIndex.countField('title'))

        myDocument = Document('0')
        myDocument.addIndexedField('title', 'titel')
        myDocument.addIndexedField('creator', 'one')
        self._luceneIndex.addToIndex(myDocument)

        my2Document = Document('1')
        my2Document.addIndexedField('title', 'een titel')
        my2Document.addIndexedField('creator', 'two')
        self._luceneIndex.addToIndex(my2Document)

        self.assertEquals([(u'een', 1), (u'titel', 2)], self._luceneIndex.countField('title'))

        self.assertEquals([(u'two', 1), (u'one', 1)], self._luceneIndex.countField('creator'))


    def xxxxxXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXxxxxxtestDeletedDocumentsInFieldCountGlitch(self):
        """This test is to make sure that values in deleted documents do not appear in the fieldcount output. This problem was noted on 26/04/2007 while working on tagging for LOREnet. The PyLucene version 2.0.0-3 has this problem, version 2.0.0 does not.

        Update 2/8/07: PyLucene 2.2 still has this problem (will it be a feature?).  Since it does only harm luceneIndex.fieldCount(), which is deprecated, we decided not to solve the problem.  In case you want to solve it, read the quite long description that comes with the javadoc for IndexWriter."""
        directory = mkdtemp()
        try:
            document = PyDocument()
            document.add(Field("id", "1", Field.Store.YES, Field.Index.TOKENIZED))
            document.add(Field("label", "value", Field.Store.NO, Field.Index.UN_TOKENIZED))

            analyzer = StandardAnalyzer()
            writer = IndexWriter(directory, analyzer, True)
            writer.addDocument(document)
            writer.close()

            reader = IndexReader.open(directory)
            self.assertFalse(reader.hasDeletions())
            self.assertEquals(1, reader.docFreq(Term('label', 'value')))

            reader.deleteDocuments(Term('id', '1'))

            self.assertTrue(reader.hasDeletions())
            self.assertEquals(1, reader.docFreq(Term('label', 'value')))
            reader.close()

            document = PyDocument()
            document.add(Field("id", "1", Field.Store.YES, Field.Index.TOKENIZED))
            document.add(Field("label", "newvalue", Field.Store.NO, Field.Index.UN_TOKENIZED))

            analyzer = StandardAnalyzer()
            writer = IndexWriter(directory, analyzer, False)
            writer.addDocument(document)
            writer.close()

            # The docFreq for Term('label', 'value') should be 0 since the record
            # got deleted. If this test fails, check the PyLucene version!
            reader = IndexReader.open(directory)
            self.assertEquals(0, reader.docFreq(Term('label', 'value')))
            self.assertEquals(1, reader.docFreq(Term('label', 'newvalue')))
            reader.close()

            writer = IndexWriter(directory, analyzer, False)
            writer.optimize()
            writer.close()

            reader = IndexReader.open(directory)
            self.assertEquals(0, reader.docFreq(Term('label', 'value')))
            self.assertEquals(1, reader.docFreq(Term('label', 'newvalue')))
            reader.close()
        finally:
            rmtree(directory)

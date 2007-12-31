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

from tempfile import mkdtemp, gettempdir
import os
from os.path import isfile, join
from shutil import rmtree
import PyLucene
from cq2utils import CQ2TestCase, CallTrace

from meresco.components.lucene.document import Document

from meresco.components.lucene.lucene import LuceneIndex
from meresco.components.lucene.document import IDFIELD
from meresco.components.lucene.cqlparsetreetolucenequery import Composer

from cqlparser import parseString

from PyLucene import Document as PyDocument, Field, IndexReader, IndexWriter, Term, TermQuery

class LuceneTest(CQ2TestCase):

    def setUp(self):
        self._tempdir = gettempdir()+'/testing'
        self.directoryName = os.path.join(self._tempdir, 'lucene-index')
        self._luceneIndex = LuceneIndex(self.directoryName, Composer({}))

    def tearDown(self):
        self._luceneIndex.close()
        if os.path.exists(self._tempdir):
            rmtree(self._tempdir)

    def testCreation(self):
        self.assertEquals(os.path.isdir(self.directoryName), True)
        self.assertTrue(IndexReader.indexExists(self.directoryName))

    def testAddToIndex(self):
        myDocument = Document('0123456789')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addToIndex(myDocument)

        hits = self._luceneIndex.executeQuery(TermQuery(Term('title', 'titel')))
        self.assertEquals(len(hits), 1)
        self.assertEquals(['0123456789'], list(hits))

    def testAddToIndexWithDuplicateField(self):
        myDocument = Document('id')
        myDocument.addIndexedField('title', 'een titel')
        myDocument.addIndexedField('title', 'een sub titel')
        self._luceneIndex.addToIndex(myDocument)

        hits = self._luceneIndex.executeQuery(TermQuery(Term('title', 'titel')))
        self.assertEquals(len(hits), 1)

        hits = self._luceneIndex.executeQuery(TermQuery(Term('title', 'sub')))
        self.assertEquals(len(hits), 1)

    def testAddTwoDocuments(self):
        myDocument = Document('1')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addToIndex(myDocument)

        myDocument = Document('2')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addToIndex(myDocument)

        hits = self._luceneIndex.executeQuery(TermQuery(Term('title', 'titel')))
        self.assertEquals(2, len(hits))

    def testAddDocumentWithTwoValuesForOneField(self):
        myDocument = Document('1')
        myDocument.addIndexedField('field1', 'value_1')
        myDocument.addIndexedField('field1', 'value_2')
        self._luceneIndex.addToIndex(myDocument)

        def check(value):
            hits = self._luceneIndex.executeQuery(TermQuery(Term('field1', value)))
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
        hits = self._luceneIndex.executeQuery(TermQuery(Term('title', 'titel')))
        self.assertEquals(2, len(hits))

        self._luceneIndex.deleteID('1')
        hits = self._luceneIndex.executeQuery(TermQuery(Term('title', 'titel')))
        self.assertEquals(1, len(hits))

    def testIndexCloses(self):
        myDocument = Document('1')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addToIndex(myDocument)
        self._luceneIndex = None
        # delete method will close the open index
        newIndex = LuceneIndex(self.directoryName, 'CQL Composer is ignored')
        newIndex.addToIndex(myDocument)
        self._luceneIndex = newIndex

    def testOptimizeClosesTheWriter(self):
        lockfile = join(self.directoryName, 'write.lock')
        self._luceneIndex.optimize()
        self.assertFalse(isfile(lockfile))

    def testExecuteCQL(self):
        mockComposer = CallTrace("CQL Composer")
        mockComposer.returnValues["compose"] = TermQuery(Term('title', 'titel'))
        index = LuceneIndex(self.directoryName, mockComposer)
        astTree = CallTrace("ASTTree")
        index.executeCQL(astTree)
        self.assertEquals(1, len(mockComposer.calledMethods))
        self.assertEquals(astTree, mockComposer.calledMethods[0].arguments[0])

    def testLoggingCQL(self):
        def logShunt(**dict):
            self.dict = dict
        self._luceneIndex.log = logShunt
        self._luceneIndex.executeCQL(parseString("term"))
        self.assertEquals({'clause': 'term'}, self.dict)
        self._luceneIndex.executeCQL(parseString("field=term"))
        self.assertEquals({'clause': 'field = term'}, self.dict)
        self._luceneIndex.executeCQL(parseString("field =/boost=1.1 term"))
        self.assertEquals({'clause': 'field =boost1.1 term'}, self.dict)
        self._luceneIndex.executeCQL(parseString("field exact term"))
        self.assertEquals({'clause': 'field exact term'}, self.dict)
        self._luceneIndex.executeCQL(parseString("term1 AND term2"))
        self.assertEquals({'clause': 'term'}, self.dict)
        self._luceneIndex.executeCQL(parseString("(term)"))
        self.assertEquals({'clause': 'term'}, self.dict)


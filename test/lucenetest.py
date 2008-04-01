
# -*- encoding: utf-8 -*-
## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
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
from time import sleep
import os
from os.path import isfile, join
from os import listdir
from shutil import rmtree

from cq2utils import CQ2TestCase, CallTrace

from meresco.components.lucene.document import Document, IDFIELD

from meresco.components.lucene.lucene import LuceneIndex
from meresco.components.dictionary import  DocumentDict, DocumentField
from meresco.components.lucene.cqlparsetreetolucenequery import Composer

from cqlparser import parseString

from PyLucene import Document as PyDocument, Field, IndexReader, IndexWriter, Term, TermQuery, MatchAllDocsQuery
from weightless import Reactor

class LuceneTest(CQ2TestCase):

    def setUp(self):
        CQ2TestCase.setUp(self)
        self.timer = CallTrace('timer')
        self._luceneIndex = LuceneIndex(
            directoryName=self.tempdir,
            cqlComposer=Composer({}),
            timer=self.timer)

        self.timerCallbackMethod = self._luceneIndex._lastUpdateTimeout

    def tearDown(self):
        self._luceneIndex.close()
        CQ2TestCase.tearDown(self)

    def testCreation(self):
        self.assertEquals(os.path.isdir(self.tempdir), True)
        self.assertTrue(IndexReader.indexExists(self.tempdir))

    def testAddToIndex(self):
        myDocument = Document('0123456789')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addDocument(myDocument)
        self.timerCallbackMethod()

        hits = self._luceneIndex.executeQuery(TermQuery(Term('title', 'titel')))
        self.assertEquals(len(hits), 1)
        self.assertEquals(['0123456789'], list(hits))

    def testAddToIndexWithDuplicateField(self):
        myDocument = Document('id')
        myDocument.addIndexedField('title', 'een titel')
        myDocument.addIndexedField('title', 'een sub titel')
        self._luceneIndex.addDocument(myDocument)
        self.timerCallbackMethod()

        hits = self._luceneIndex.executeQuery(TermQuery(Term('title', 'titel')))
        self.assertEquals(len(hits), 1)

        hits = self._luceneIndex.executeQuery(TermQuery(Term('title', 'sub')))
        self.assertEquals(len(hits), 1)

    def testAddTwoDocuments(self):
        myDocument = Document('1')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addDocument(myDocument)

        myDocument = Document('2')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addDocument(myDocument)
        self.timerCallbackMethod()

        hits = self._luceneIndex.executeQuery(TermQuery(Term('title', 'titel')))
        self.assertEquals(2, len(hits))

    def testAddDocumentWithTwoValuesForOneField(self):
        myDocument = Document('1')
        myDocument.addIndexedField('field1', 'value_1')
        myDocument.addIndexedField('field1', 'value_2')
        self._luceneIndex.addDocument(myDocument)

        self.timerCallbackMethod()

        def check(value):
            hits = self._luceneIndex.executeQuery(TermQuery(Term('field1', value)))
            self.assertEquals(1, len(hits))
        check('value_1')
        check('value_2')

    def testAddUTF8Document(self):
        myDocument = Document('0123456789')
        myDocument.addIndexedField('title', 'BijenkorfÂ´s')
        self._luceneIndex.addDocument(myDocument)

    def testAddDocumentWithFailure(self):
        self._luceneIndex.close()
        myIndex = LuceneIndex(
            directoryName=self.tempdir,
            cqlComposer=Composer({}),
            timer=Reactor())
        class MyException(Exception):
            pass
        myDocument = Document('1')
        myDocument.addIndexedField('aap', 'noot')
        myIndex.addDocument(myDocument)
        def validate():
            raise MyException('Boom')
        myDocument.validate = validate
        try:
            myIndex.addDocument(myDocument)
            self.fail()
        except MyException:
            pass

        my2Document = Document('2')
        my2Document.addIndexedField('aap', 'noot')
        myIndex.addDocument(my2Document)
        

    def testDeleteFromIndex(self):
        myDocument = Document('1')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addDocument(myDocument)

        myDocument = Document('2')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addDocument(myDocument)
        self.timerCallbackMethod()

        hits = self._luceneIndex.executeQuery(TermQuery(Term('title', 'titel')))
        self.assertEquals(2, len(hits))

        self._luceneIndex.delete('1')

        hits = self._luceneIndex.executeQuery(TermQuery(Term('title', 'titel')))
        self.assertEquals(2, len(hits))

        self.timerCallbackMethod()
        hits = self._luceneIndex.executeQuery(TermQuery(Term('title', 'titel')))
        self.assertEquals(1, len(hits))

    def testAddDeleteWithoutReopenInBetween(self):
        myDocument = Document('1')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addDocument(myDocument)

        self._luceneIndex.delete('1')
        self.timerCallbackMethod()
        hits = self._luceneIndex.executeQuery(TermQuery(Term('title', 'titel')))
        self.assertEquals(0, len(hits))


    def testIndexCloses(self):
        index = LuceneIndex(self.tempdir + '/x', cqlComposer=None, timer=self.timer)
        myDocument = Document('1')
        myDocument.addIndexedField('title', 'een titel')
        index.addDocument(myDocument)
        # The next call shouldn't be necessary, but ....
        index.__del__()
        index = None
        self.assertFalse(isfile(self.tempdir + '/x/write.lock'))

    def testExecuteCQLUsesComposer(self):
        mockComposer = CallTrace("CQL Composer")
        mockComposer.returnValues["compose"] = TermQuery(Term('title', 'titel'))
        index = LuceneIndex(directoryName=self.tempdir+'/x', cqlComposer=mockComposer, timer=None)
        astTree = CallTrace("AST")
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
        self.assertEquals({'clause': 'field =/boost=1.1 term'}, self.dict)
        self._luceneIndex.executeCQL(parseString("field exact term"))
        self.assertEquals({'clause': 'field exact term'}, self.dict)
        self._luceneIndex.executeCQL(parseString("term1 AND term2"))
        self.assertEquals({'clause': 'term1'}, self.dict)
        self._luceneIndex.executeCQL(parseString("(term)"))
        self.assertEquals({'clause': 'term'}, self.dict)

    def testUpdateSetsTimer(self):
        myDocument = Document('1')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addDocument(myDocument) # this must trigger a timer
        self.assertEquals('addTimer', self.timer.calledMethods[0].name)
        self.assertEquals(1, self.timer.calledMethods[0].args[0])
        timeCallback = self.timer.calledMethods[0].args[1]
        self.assertTrue(timeCallback)

    def testUpdateRESetsTimer(self):
        self.timer.returnValues['addTimer'] = 'aToken'
        myDocument = Document('1')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addDocument(myDocument) # this must trigger a timer
        self._luceneIndex.addDocument(myDocument) # this must REset the timer
        self.assertEquals(['addTimer', 'removeTimer', 'addTimer'],
            [method.name for method in self.timer.calledMethods])
        self.assertEquals('aToken', self.timer.calledMethods[1].args[0])

    def testOptimizeOnTimeOut(self):
        self.timer.returnValues['addTimer'] = 'aToken'
        myDocument = Document('1')
        myDocument.addIndexedField('title', 'een titel')
        self._luceneIndex.addDocument(myDocument)
        timeCallback = self.timer.calledMethods[0].args[1]
        self.assertEquals(0, len(list(self._luceneIndex.executeCQL(parseString("title=titel")))))
        timeCallback()
        self.assertEquals(1, len(list(self._luceneIndex.executeCQL(parseString("title=titel")))))
        # after callback the old timer will not be removed
        self._luceneIndex.addDocument(myDocument)
        self.assertEquals(['addTimer', 'addTimer'],
            [method.name for method in self.timer.calledMethods])

    def testStart(self):
        intercept = CallTrace('Interceptor')
        self._luceneIndex.addObserver(intercept)

        self._luceneIndex.start()

        self.assertEquals(1, len(intercept.calledMethods))
        self.assertEquals('indexStarted', intercept.calledMethods[0].name)

    def testDocIdsAssumptions(self):
        self._luceneIndex._timer = CallTrace()

        def addDocs(min, max):
            for x in range(min, max):
                doc = Document(str(x))
                doc.addIndexedField('field', 'required')
                self._luceneIndex.addDocument(doc)
        addDocs(0, 150) #halverwege segment 2. v. grootte honderd
        self._luceneIndex._reopenIndex()

        hits = self._luceneIndex._executeQuery(MatchAllDocsQuery())
        self.assertEquals(range(150), hits.bitMatrixRow().asPythonListForTesting())

        #schiet verschillende smaken gaten in segment 1. (wat hierbij al afgerond is)
        for x in range(0, 31, 2):
            self._luceneIndex.delete(str(x))
        for x in range(70, 100):
            self._luceneIndex.delete(str(x))

        #in tweede segment v. grootte honderd (een nog niet afgerond segment)
        for x in range(100, 120, 2):
            self._luceneIndex.delete(str(x))
        for x in range(130, 140):
            self._luceneIndex.delete(str(x))

        addDocs(150, 220) #well into segment 3 v. grootte honderd.

        self._luceneIndex._reopenIndex()

        docIds = []
        for id in range(220):
            hits = self._luceneIndex._executeQuery(TermQuery(Term(IDFIELD, str(id))))
            currentDocIds = hits.bitMatrixRow().asPythonListForTesting()
            if currentDocIds:
                currentDocId = currentDocIds[0]
                docIds.append(currentDocId)
                if id < 100: #segment that had no chance to optimize
                    self.assertEquals(id, currentDocId) #not optimized, so still identical
                else:
                    self.assertTrue(currentDocId < id, "expecting currentDocId to be smaller than id, because currentDocIds should be reused, but: not  %s < %s" % (currentDocId, id))

        self.assertEquals(sorted(docIds), docIds)

        #uit onderstaand blok kan je lezen dat bij het mergen van een segment x nieuwe nummers gebruikt gaan worden, te beginnen bij het hoogste nummer van ('vol' of 'gatenkaas') vorige segment
        self.assertFalse(0 in docIds)
        self.assertFalse(70 in docIds)
        self.assertFalse(99 in docIds)
        self.assertTrue(100 in docIds) #hoewel weggegooid, is deze hergebruikt
        self.assertTrue(130 in docIds) #hoewel weggegooid, is deze hergebruikt

        def luceneState():
            return self._luceneIndex._executeQuery(MatchAllDocsQuery()).bitMatrixRow().asPythonListForTesting()

        #the following tests that deletes without add do not trigger merges/shifting of docids
        lastDocIds = luceneState()
        for x in range(220):
            self._luceneIndex.delete(str(x))
            self._luceneIndex._reopenIndex()
            currentDocIds = luceneState()
            if currentDocIds == lastDocIds:
                continue
            self.assertEquals(1, len(lastDocIds) - len(currentDocIds))
            self.assertEquals(lastDocIds[1:], currentDocIds)
            lastDocIds = currentDocIds


    def testMerging(self):
        """
            After 10 added documents, a new segment file is created.
            After the 10th segment, the segments are merged into 1 segment
        """
        self._luceneIndex._reopenIndex = lambda: None #turn off auto-reopens

        def addDocument(number):
            d = Document(str(number))
            d.addIndexedField('field', 'value')
            self._luceneIndex.addDocument(d)

        fileCount = 3
        docsAdded = 0
        segmentMerges = 0
        for i in range(300):
            addDocument(i)
            docsAdded += 1
            newFileCount = len(listdir(self.tempdir))

            # less files, seperate segments got merged into a larger segment
            if newFileCount < fileCount:
                segmentMerges += 1
                self.assertEquals(100*segmentMerges, i+1)   # i = 0 based

            # after 10 added documents, a new file should have been born
            if newFileCount != fileCount:
                self.assertEquals(10, docsAdded)
                fileCount = newFileCount
                docsAdded = 0

    #bitwise extension version:
    #def testCallAddDocumentAfterReopen(self):
        #d = Document("anId")
        #d.addIndexedField('field', 'value')
        #d.pokedDict = DocumentDict()
        #d.pokedDict.addField(DocumentField('field', 'value'))
        #self._luceneIndex.addDocument(d)
        #observer = CallTrace()
        #self._luceneIndex.addObserver(observer)
        #self._luceneIndex._reopenIndex()
        #self.assertEquals(1, len(observer.calledMethods))
        #self.assertEquals('addDocument', observer.calledMethods[0].name)
        #self.assertEquals(0, observer.calledMethods[0].args[0])
        #self.assertEquals([('field', set(['value']))], observer.calledMethods[0].args[1])


    def testAddIsAlsoDeleteCausesBug(self):
        from meresco.components.dictionary import DocumentDict, DocumentField, Dict2Doc
        reopen = self._luceneIndex._reopenIndex
        self._luceneIndex._reopenIndex = lambda: None

        def add(value):
            dd = DocumentDict()
            dd.add("value", value)
            doc = Dict2Doc()._dict2Doc("theIdIsTheSame", dd)
            self._luceneIndex.addDocument(doc)

        for i in range(100):
            add("a" + str(i))
            reopen()

    def testMultipleAddsWithoutReopenIsEvenDifferent(self):
        from meresco.components.dictionary import DocumentDict, DocumentField, Dict2Doc
        reopen = self._luceneIndex._reopenIndex
        self._luceneIndex._reopenIndex = lambda: None

        def add(value):
            dd = DocumentDict()
            dd.add("value", value)
            doc = Dict2Doc()._dict2Doc("theIdIsTheSame", dd)
            self._luceneIndex.addDocument(doc)

        for i in range(100):
            add("a" + str(i))

        reopen()

    def testAnalyser(self):
        myDocument = Document('id0')
        myDocument.addIndexedField('field', 'a')
        myDocument.addIndexedField('field', 'vAlUe')
        self._luceneIndex.addDocument(myDocument)
        self.timerCallbackMethod()

        hits = self._luceneIndex.executeQuery(TermQuery(Term('field', 'a')))
        self.assertEquals(len(hits), 1)
        self.assertEquals(['id0'], list(hits))

        hits = self._luceneIndex.executeQuery(TermQuery(Term('field', 'value')))
        self.assertEquals(len(hits), 1)
        self.assertEquals(['id0'], list(hits))

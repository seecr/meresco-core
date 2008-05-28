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
from unittest import TestCase
from cq2utils import CQ2TestCase

from meresco.components.drilldown.lucenerawdocsets import LuceneRawDocSets
from meresco.components.lucene.lucene import LuceneIndex
from meresco.components.lucene.document import Document

from timerfortestsupport import TimerForTestSupport
from PyLucene import IndexReader

class LuceneRawDocSetsTest(CQ2TestCase):

    #Helper functions:
    def addUntokenized(self, documents):
        index = LuceneIndex(self.tempdir, 'CQL Composer ignored', timer=TimerForTestSupport())
        for docId, fields in documents:
            myDocument = Document(docId)
            for field, value in fields.items():
                myDocument.addIndexedField(field, value, tokenize = False)
            index.addDocument(myDocument)
        #index._writer.optimize()
        index.close()

    def testCreateDocSetsFromReader(self):
        self.addUntokenized([
            ('1', {'field_0': 'this is term_0', 'field_1': 'inquery'}),
            ('2', {'field_0': 'this is term_0', 'field_1': 'inquery'}),
            ('3', {'field_0': 'this is term_1', 'field_1': 'inquery'}),
            ('4', {'field_0': 'this is term_2', 'field_1': 'cannotbefound'})])
        reader = IndexReader.open(self.tempdir)

        converter = LuceneRawDocSets(reader, ['field_0', 'field_1', 'none_existing_field'])
        docsets = [(field, [(term, list(docIds))
            for term, docIds in terms])
                for field, terms in converter.getDocSets()]
        self.assertEquals(3, len(docsets), docsets)
        self.assertEquals([
            ('field_0', [(u'this is term_0', [0, 1]),(u'this is term_1', [2]), (u'this is term_2', [3])]),
            ('field_1', [(u'cannotbefound', [3]), (u'inquery', [0, 1, 2])]),
            ('none_existing_field', [])], docsets)

    def testListOperatorNotWorkingBug(self):
        """Some parts of execution may not be deferred using generators. Since they depend on pointers and need to be read immediately before the pointer is shifted."""
        self.addUntokenized([
            ('1', {'field_0': 'this is term_0'}),
            ('2', {'field_0': 'this is term_1'})])
        reader = IndexReader.open(self.tempdir)
        converter = LuceneRawDocSets(reader, ['field_0'])
        fieldname, terms = converter.getDocSets().next()
        listTerms = list(terms)
        for i, (term, docIds) in enumerate(listTerms):
            self.assertEquals('this is term_%s' % i, term)
            self.assertEquals([i], list(docIds))

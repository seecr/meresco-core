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
from tempfile import gettempdir
from shutil import rmtree
from os.path import join

from meresco.components.drilldown.lucenerawdocsets import LuceneRawDocSets
from meresco.components.lucene.lucene import LuceneIndex
from meresco.components.lucene.document import Document

#Helper functions:
def addUntokenized(index, documents):
    for docId, fields in documents:
        myDocument = Document(docId)
        for field, value in fields.items():
            myDocument.addIndexedField(field, value, tokenize = False)
        index.addToIndex(myDocument)

class LuceneRawDocSetsTest(TestCase):
    def setUp(self):
        self._tempdir = gettempdir() + '/testing'
        self._directoryName = join(self._tempdir, 'lucene-index')
        self._luceneIndex = LuceneIndex(self._directoryName, 'CQL Composer ignored')

    def tearDown(self):
        self._luceneIndex = None
        rmtree(self._tempdir)

    def testCreateDocSetsFromReader(self):
        addUntokenized(self._luceneIndex, [
            ('1', {'field_0': 'this is term_0', 'field_1': 'inquery'}),
            ('2', {'field_0': 'this is term_0', 'field_1': 'inquery'}),
            ('3', {'field_0': 'this is term_1', 'field_1': 'inquery'}),
            ('4', {'field_0': 'this is term_2', 'field_1': 'cannotbefound'})])

        converter = LuceneRawDocSets(self._luceneIndex._getReader(), ['field_0', 'field_1'])
        docsets = [(field, [(term, list(docIds))
            for term, docIds in terms])
                for field, terms in converter.getDocSets()]
        self.assertEquals(2, len(docsets))
        self.assertEquals([('field_0', [(u'this is term_0', [0, 1]), (u'this is term_1', [2]), (u'this is term_2', [3])]), ('field_1', [(u'cannotbefound', [3]), (u'inquery', [0, 1, 2])])], docsets)

    def testListOperatorNotWorkingBug(self):
        """Some parts of execution may not be deferred using generators. Since they depend on pointers and need to be read immediately before the pointer is shifted."""
        addUntokenized(self._luceneIndex, [
            ('1', {'field_0': 'this is term_0'}),
            ('2', {'field_0': 'this is term_1'})])

        converter = LuceneRawDocSets(self._luceneIndex._getReader(), ['field_0'])
        fieldname, terms = converter.getDocSets().next()
        listTerms = list(terms)
        for i, (term, docIds) in enumerate(listTerms):
            self.assertEquals('this is term_%s' % i, term)
            self.assertEquals([i], list(docIds))

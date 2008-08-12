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
from cq2utils import CallTrace
from meresco.framework import be, Transparant, Observable
from meresco.framework import TransactionScope, TransactionFactory

from meresco.components.lucene import Fields2LuceneDocumentTx

class Fields2LuceneDocumentTest(TestCase):

    def setUp(self):
        self.observert = CallTrace('Observert', ignoredAttributes=['_observers'])
        class Splitter(Transparant):
            def addFields(this, tupleList):
                for item in tupleList:
                    this.any.addField(*item)

        dna = \
            (Observable(),
                (TransactionScope(),
                    (Splitter(),
                        (TransactionFactory(lambda tx: Fields2LuceneDocumentTx(tx, untokenized=['b'])),
                            (self.observert,)
                        )
                    )
                )
            )
        self.body = be(dna)

    def testOne(self):
        list(self.body.all.addFields([('__id__', 'ID'), ('a', '1'), ('b', '2'), ('c', '3')]))
        self.assertEquals(3, len(self.observert.calledMethods))
        self.assertEquals('begin()', str(self.observert.calledMethods[0]))
        self.assertEquals('addDocument(<meresco.components.lucene.document.Document>)', str(self.observert.calledMethods[1]))
        self.assertEquals('commit()', str(self.observert.calledMethods[2]))
        document = self.observert.calledMethods[1].args[0]
        self.assertTrue('a' in document.fields())
        self.assertTrue('b' in document.fields())
        self.assertTrue('c' in document.fields())
        self.assertTrue('__id__' in document.fields())

    def testMultipleValuesForSameKey(self):
        list(self.body.all.addFields([('__id__', 'ID'), ('a', 'TermOne'), ('a', 'TermTwo'), ('b', '3')]))
        self.assertEquals(3, len(self.observert.calledMethods))
        self.assertEquals('begin()', str(self.observert.calledMethods[0]))
        self.assertEquals('addDocument(<meresco.components.lucene.document.Document>)', str(self.observert.calledMethods[1]))
        self.assertEquals('commit()', str(self.observert.calledMethods[2]))
        document = self.observert.calledMethods[1].args[0]
        self.assertEquals([u'TermOne', u'TermTwo'],  document._document.getValues('a'))

    def testTokenizedIsNotForgotten(self):
        list(self.body.all.addFields([('__id__', 'ID'), ('a', '1'), ('a', 'termone termtwo'), ('b', 'termone termtwo')]))
        document = self.observert.calledMethods[1].args[0]
        self.assertTrue(document._document.getField('a').isTokenized())
        self.assertFalse(document._document.getField('b').isTokenized())

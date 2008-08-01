from unittest import TestCase
from cq2utils import CallTrace
from meresco.framework import be, Transparant, Observable
from meresco.framework import TransactionScope

from meresco.components.lucene import Fields2LuceneDocument

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
                        (Fields2LuceneDocument(untokenized=['b']),
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


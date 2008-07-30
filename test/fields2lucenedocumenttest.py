from unittest import TestCase
from cq2utils import CallTrace
from meresco.framework import be, Transparant
from meresco.framework import TransactionScope

from meresco.components.lucene import Fields2LuceneDocument

class Fields2LuceneDocumentTest(TestCase):

    def setUp(self):
        self.observert = CallTrace('Observert')
        class Splitter(Transparant):
            def addFields(this, tupleList):
                for item in tupleList:
                    this.any.addField(*item)

        dna = [
            (TransactionScope(), [
                (Splitter(), [
                    (Fields2LuceneDocument(tokenized=['b','c']), [
                        self.observert
                    ])
                ])
            ])
        ]
        self.body = be(dna)

    def testOne(self):
        list(self.body.all.addFields([('__id__', 'ID'), ('a', '1'), ('b', '2'), ('c', '3')]))
        self.assertEquals(1, len(self.observert.calledMethods))
        self.assertEquals('addDocument', self.observert.calledMethods[0].name)
        document = self.observert.calledMethods[0].args[0]
        self.assertTrue('a' in document.fields())
        self.assertTrue('b' in document.fields())
        self.assertTrue('c' in document.fields())
        self.assertTrue('__id__' in document.fields())

    def testMultipleValuesForSameKey(self):
        list(self.body.all.addFields([('__id__', 'ID'), ('a', '1'), ('a', '2'), ('b', '3')]))
        self.assertEquals(1, len(self.observert.calledMethods))
        self.assertEquals('addDocument(<meresco.components.lucene.document.Document>)', str(self.observert.calledMethods[0]))
        document = self.observert.calledMethods[0].args[0]
        self.assertEquals([u'1', u'2'],  document._document.getValues('a'))


from cq2utils import CQ2TestCase, CallTrace

from meresco.framework import be, Transparant
from meresco.framework import TransactionScope

from meresco.components.lucene import Fields2LuceneDocument

class Fields2LuceneDocumentTest(CQ2TestCase):
    def testOne(self):
        observert = CallTrace('Observert')

        class Splitter(Transparant):
            def addFields(this, aDictionary):
                for item in aDictionary.items():
                    this.any.addField(*item)

        dna = [
            (TransactionScope(), [
                (Splitter(), [
                    (Fields2LuceneDocument(tokenized=['b','c']), [
                        observert
                    ])
                ])
            ])
        ]
        body = be(dna)
        list(body.all.addFields({'__id__': 'ID','a': 1, 'b': 2, 'c': 3}))

        self.assertEquals(1, len(observert.calledMethods))
        self.assertEquals('addDocument', observert.calledMethods[0].name)



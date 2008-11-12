
from cq2utils import CQ2TestCase, CallTrace

from meresco.components.oai import Fields2OaiRecordTx

class Fields2OaiRecordTest(CQ2TestCase):
    def testOne(self):
        transaction = CallTrace('Transaction')
        rm = CallTrace('ResourceManager')
        rm.tx = transaction
        rm.do = rm
        transaction.locals = {'id':'identifier'}
        
        tx = Fields2OaiRecordTx(rm)
        
        tx.addField('set', ('setSpec', 'setName'))
        tx.addField('metadataFormat', ('prefix', 'schema', 'namespace'))
        tx.commit()

        self.assertEquals(1, len(rm.calledMethods))
        self.assertEquals('addOaiRecord', rm.calledMethods[0].name)
        self.assertEquals({'identifier':'identifier',
                'metadataFormats': set([('prefix', 'schema', 'namespace')]),
                'sets': set([('setSpec', 'setName')])},
            rm.calledMethods[0].kwargs)
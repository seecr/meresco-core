
from cq2utils import CQ2TestCase, CallTrace

from meresco.components import Fields2XmlTx
from meresco.components.fields2xml import Fields2XmlException, generateXml
from amara.binderytools import bind_string

class Fields2XmlTest(CQ2TestCase):
    def testOne(self):
        transaction = CallTrace('Transaction')
        transactionDo = CallTrace('TransactionDo')
        transaction.do = transactionDo
        
        f = Fields2XmlTx(transaction, 'extra')

        f.addField('__id__', 'identifier')
        f.addField('key.sub', 'value')
        f.finalize()

        self.assertEquals(['store'], [m.name for m in transactionDo.calledMethods])
        self.assertEquals(('identifier', 'extra', '<extra><key><sub>value</sub></key></extra>'), transactionDo.calledMethods[0].args)

    def testPartNameIsDefinedAtInitialization(self):
        transaction = CallTrace('Transaction')
        transactionDo = CallTrace('TransactionDo')
        transaction.do = transactionDo
        
        f = Fields2XmlTx(transaction, 'partName')
        f.addField('__id__', 'otherIdentifier')
        f.addField('key.sub', 'value')
        f.finalize()
        
        self.assertEquals('otherIdentifier', transactionDo.calledMethods[0].args[0])
        self.assertEquals('partName', transactionDo.calledMethods[0].args[1])
        xml = bind_string(transactionDo.calledMethods[0].args[2])
        self.assertEquals('partName', str(xml.childNodes[0].localName))

    def testIllegalPartNameRaisesException(self):
        for name in ['this is wrong', '%%@$%*^$^', '/slash', 'dot.dot']:
            try:
                Fields2XmlTx('ignored', name)
                self.fail('Expected error for ' + name)
            except Fields2XmlException, e:
                self.assertTrue(name in str(e))

    def testGenerateOneKeyXml(self):
        self.assertEquals('<key>value</key>', generateXml([('key','value')]))

    def testGenerateOneSubKeyXml(self):
        self.assertEquals('<key><sub>value</sub></key>', generateXml([('key.sub','value')]))
   
    def testGenerateTwoSubKeyXml(self):
        self.assertEquals('<key><sub>value</sub><sub2>value2</sub2></key>', generateXml([('key.sub','value'), ('key.sub2','value2')]))

    def testGenerateOtherParentKeyXml(self):
        self.assertEquals('<a><b>value</b></a><c><d>value2</d></c>', generateXml([('a.b','value'), ('c.d','value2')]))

    def testGenerateXml(self):
        self.assertEquals('<a><b><c><d>DDD</d><e>EEE</e></c><c>CCC</c><f>FFF</f><c><d>DDD</d></c></b></a>', generateXml([('a.b.c.d','DDD'), ('a.b.c.e','EEE'), ('a.b.c', 'CCC'),('a.b.f', 'FFF'), ('a.b.c.d', 'DDD')]))

    def testEscapeTagNamesAndValues(self):
        try:
            generateXml([('k/\\.sub','value')])
            self.fail()
        except Fields2XmlException, e:
            self.assertTrue('k/\\.sub' in str(e))


        self.assertEquals('<key>&lt;/tag&gt;</key>', generateXml([('key','</tag>')]))
        
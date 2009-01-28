
from cq2utils import CQ2TestCase, CallTrace
from merescocore.components import CQLConversion
from merescocore.framework import Observable, be
from cqlparser import parseString


class CQLConversionTest(CQ2TestCase):
    
    def testCQLContextSetConversion(self):
        myDict = {'fieldone':'translatedfield'}
        observer = CallTrace('observer')
        o = be((Observable(),
            (CQLConversion(lambda fieldname:myDict.get(fieldname, fieldname)),
                (observer,)
            )
        ))
        o.do.whatever(parseString('afield = value'))
        self.assertEquals(1, len(observer.calledMethods))
        self.assertEquals('whatever', observer.calledMethods[0].name)
        self.assertEquals((parseString('afield = value'),), observer.calledMethods[0].args)

    def testCQLCanConvert(self):
        c = CQLConversion(lambda fieldname: 'myfield')
        self.assertTrue(c._canConvert(parseString('field = value')))
        self.assertFalse(c._canConvert('other object'))

    def testCQLConvert(self):
        c = CQLConversion(lambda fieldname: 'myfield')
        self.assertEquals(parseString('myfield = value'), c._convert(parseString('otherfield = value')))

from cq2utils import CQ2TestCase, CallTrace

from meresco.framework import be, Observable
from meresco.components import CopyField


class CopyFieldTest(CQ2TestCase):
    def setUp(self):
        CQ2TestCase.setUp(self)
        self.observert = CallTrace('Observer')

    def testCopyField(self):
        dna = be(
            (Observable(),
                (CopyField(lambda f: True, lambda n: n+'.'+n),
                    (self.observert, )
                )
            )
        )

        dna.do.addField(name='fieldname', value="x")
        self.assertEquals(2, len(self.observert.calledMethods))

        self.assertEquals("addField('fieldname.fieldname', 'x')", str(self.observert.calledMethods[0]))
        self.assertEquals("addField('fieldname', 'x')", str(self.observert.calledMethods[1]))

    def testCopyFieldWithTransform(self):
        dna = be(
            (Observable(),
                (CopyField(lambda f: True, lambda n: n, transform=lambda value: 'transform ' + value),
                    (self.observert, )
                )
            )
        )

        dna.do.addField(name='f', value="x")
        self.assertEquals(2, len(self.observert.calledMethods))

        self.assertEquals("addField('f', 'transform x')", str(self.observert.calledMethods[0]))


    def testDoNotCopyFieldForTransformWithNoneResult(self):
        dna = be(
            (Observable(),
                (CopyField(lambda f: True, lambda n: n, transform=lambda value: None),
                    (self.observert, )
                )
            )
        )

        dna.do.addField(name='f', value="x")
        self.assertEquals(1, len(self.observert.calledMethods))


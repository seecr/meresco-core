from cq2utils import CQ2TestCase, CallTrace

from meresco.framework import be, Observable
from meresco.components import RenameField, TransformField, FilterField


class FieldletsTest(CQ2TestCase):
    def setUp(self):
        CQ2TestCase.setUp(self)
        self.observert = CallTrace('Observer')

    def testRenameField(self):
        dna = be(
            (Observable(),
                (RenameField(lambda name: name + '.fieldname'),
                    (self.observert, )
                )
            )
        )

        dna.do.addField(name='fieldname', value="x")
        self.assertEquals(1, len(self.observert.calledMethods))

        self.assertEquals("addField('fieldname.fieldname', 'x')", str(self.observert.calledMethods[0]))

    def testTransformFieldWithTransform(self):
        dna = be(
            (Observable(),
                (TransformField(lambda value: 'transform ' + value),
                    (self.observert, )
                )
            )
        )

        dna.do.addField(name='f', value="x")
        self.assertEquals(1, len(self.observert.calledMethods))

        self.assertEquals("addField('f', 'transform x')", str(self.observert.calledMethods[0]))


    def testDoNotTransformFieldForTransformWithNoneResult(self):
        dna = be(
            (Observable(),
                (TransformField(lambda value: None),
                    (self.observert, )
                )
            )
        )

        dna.do.addField(name='f', value="x")
        self.assertEquals(0, len(self.observert.calledMethods))

    def testIntegration(self):
        dna = be(
            (Observable(),
                (self.observert,),
                (FilterField(lambda name:name in ['name1']),
                    (RenameField(lambda name:'drilldown.'+name),
                        (self.observert,)
                    )
                ),
                (FilterField(lambda name:name in ['name2']),
                    (TransformField(lambda value: value.upper()),
                        (RenameField(lambda name:'normalize.'+name),
                            (self.observert,)
                        )
                    ),
                    (TransformField(lambda value: None),
                        (RenameField(lambda name:'normalize2.'+name),
                            (self.observert,)
                        )
                    ),
                    (TransformField(lambda value: value),
                        (RenameField(lambda name:'normalize3.'+name),
                            (self.observert,)
                        )
                    )
                )
            )
        )
        dna.do.addField('name1', 'value1')
        dna.do.addField('name2', 'value2')
        dna.do.addField('name3', 'value3')
        self.assertEquals(6, len(self.observert.calledMethods))

        self.assertEquals([
            "addField('name1', 'value1')",
            "addField('drilldown.name1', 'value1')",
            "addField('name2', 'value2')",
            "addField('normalize.name2', 'VALUE2')",
            "addField('normalize3.name2', 'value2')",
            "addField('name3', 'value3')",
            ], [str(m) for m in self.observert.calledMethods])


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
from cq2utils import CQ2TestCase, CallTrace

from merescocore.framework import be, Observable
from merescocore.components import RenameField, TransformFieldValue, FilterField


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

    def testTransformFieldValueWithTransform(self):
        dna = be(
            (Observable(),
                (TransformFieldValue(lambda value: 'transform ' + value),
                    (self.observert, )
                )
            )
        )

        dna.do.addField(name='f', value="x")
        self.assertEquals(1, len(self.observert.calledMethods))

        self.assertEquals("addField('f', 'transform x')", str(self.observert.calledMethods[0]))


    def testDoNotTransformFieldValueForTransformWithNoneResult(self):
        dna = be(
            (Observable(),
                (TransformFieldValue(lambda value: None),
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
                    (TransformFieldValue(lambda value: value.upper()),
                        (RenameField(lambda name:'normalize.'+name),
                            (self.observert,)
                        )
                    ),
                    (TransformFieldValue(lambda value: None),
                        (RenameField(lambda name:'normalize2.'+name),
                            (self.observert,)
                        )
                    ),
                    (TransformFieldValue(lambda value: value),
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


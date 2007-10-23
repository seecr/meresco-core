from meresco.components.dictionary.transform import CleanSplit, years
from meresco.components.dictionary import Transform, DocumentField

from cq2utils import CallTrace

import unittest

class TransformTest(unittest.TestCase):

    def testBasicBehavior(self):
        transform = Transform('some.source', 'target', CleanSplit(';'))
        self.assertEquals([
            DocumentField('target', 'some'),
            DocumentField('target', 'thing')],
            list(transform.fieldsForField(DocumentField('some.source', 'some;thing'))))

    def testYears(self):
        self.assertEquals([], years('garbage'))
        self.assertEquals(['2000'], years('2000'))
        self.assertEquals(['2000', '2001'], years('2000-2001'))
        self.assertEquals(['2000'], years('2000-01-01'))
        self.assertEquals(['2000'], years('2000-01-01T23:32:12Z'))

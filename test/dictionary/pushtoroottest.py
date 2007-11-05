from meresco.components.dictionary.pushtoroot import PushToRoot
from meresco.components.dictionary import Transform, DocumentField

from cq2utils import CallTrace

import unittest

class PushToRootTest(unittest.TestCase):

    def testBasicBehavior(self):
        pushToRoot = PushToRoot()
        result = set(pushToRoot.fieldsForField(DocumentField('root.zero.one.two', 'field contents', additionalParam="propagated")))
        self.assertEquals(DocumentField('a', 'a', x="a"), DocumentField('a', 'a', x='a'))
        self.assertEquals(set([
            DocumentField('root', 'field contents', additionalParam="propagated"),
            DocumentField('root.zero', 'field contents', additionalParam="propagated"),
            DocumentField('root.zero.one', 'field contents', additionalParam="propagated"),
            DocumentField('root.zero.one.two', 'field contents', additionalParam="propagated")]),
            result)


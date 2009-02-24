
from cq2utils import CQ2TestCase

from merescocore.components import RenameCqlIndex
from cqlparser import parseString

class RenameCqlIndexTest(CQ2TestCase):
    def testConvert(self):
        rename = RenameCqlIndex(lambda name: 'other'+name)
        self.assertEquals(parseString('otherfield = value'), rename(parseString('field = value')))

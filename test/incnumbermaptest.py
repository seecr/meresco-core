


from unittest import TestCase
from meresco.components import IncNumberMap, IncNumberMapException

class IncNumberMapTest(TestCase):

    def setUp(self):
        self._incNumberMap = IncNumberMap()

    def testZero(self):
        try:
            self._incNumberMap.get(0)
            self.fail()
        except IncNumberMapException:
            pass

    def testOneElement(self):
        result = self._incNumberMap.add(0)
        self.assertEquals(0, result)
        self.assertEquals(0, self._incNumberMap.get(0))

    def testMultipleElements(self):
        result = self._incNumberMap.add(0)
        self.assertEquals(0, result)

        result = self._incNumberMap.add(1)
        self.assertEquals(1, result)
        self.assertEquals(0, self._incNumberMap.get(0))
        self.assertEquals(1, self._incNumberMap.get(1))

    def testReaddingForbidden(self):
        self._incNumberMap.add(0)
        try:
            self._incNumberMap.add(0)
            self.fail()
        except IncNumberMapException:
            pass

    def testDeleteAtBeginning(self):
        self._incNumberMap.add(0)
        self._incNumberMap.add(1)
        self._incNumberMap.deleteAndCollapse(0)
        self.assertEquals(1, self._incNumberMap.get(0))

    def testDeleteAtEnd(self):
        self._incNumberMap.add(0)
        self._incNumberMap.add(1)
        self._incNumberMap.deleteAndCollapse(1)
        self.assertEquals(0, self._incNumberMap.get(0))




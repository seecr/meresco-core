


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

    def testDelete(self):
        self._incNumberMap.add(0)
        self._incNumberMap.add(1)
        self._incNumberMap.delete(0)
        try:
            self._incNumberMap.get(0)
            self.fail()
        except IncNumberMapException:
            pass
        self.assertEquals(1, self._incNumberMap.get(1))
        self._incNumberMap.collapse(1)
        self.assertEquals(1, self._incNumberMap.get(0))

    def testDeleteMultiple(self):
        self._incNumberMap.add(0)
        self._incNumberMap.add(1)
        self._incNumberMap.add(2)
        self._incNumberMap.delete(0)
        self._incNumberMap.delete(2)

        self.assertEquals(1, self._incNumberMap.get(1))
        self._incNumberMap.collapse(2)
        self.assertEquals(1, self._incNumberMap.get(0))

        try:
            self._incNumberMap.get(1)
            self.fail()
        except IncNumberMapException:
            pass



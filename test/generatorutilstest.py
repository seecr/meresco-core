from unittest import TestCase

from meresco.framework.generatorutils import Peek, peek

class GeneratorUtilsTest(TestCase):

	def testEmptyGenerator(self):
		responses = Peek((i for i in []))
		self.assertTrue(responses.empty())

	def testNonEmptyGenerator(self):
		responses = Peek((i for i in [1,2,3]))
		self.assertFalse(responses.empty())
		result = list(responses)
		self.assertEquals([1,2,3], result)

	def testAlternativePeekNotEmpty(self):
		result = list(peek(1, (i for i in [2]), 3))
		self.assertEquals([1,2,3], result)

	def testAlternativePeekEmpty(self):
		result = list(peek(1, (i for i in []), 3))
		self.assertEquals([], result)

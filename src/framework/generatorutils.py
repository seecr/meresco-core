class Peek:
	def __init__(self, generator):
		self._generator = generator
		try:
			self._first = generator.next()
		except StopIteration:
			pass

	def empty(self):
		return not hasattr(self, '_first')

	def __iter__(self):
		while True:
			yield self._first
			self._first = self._generator.next()

def decorate(before, generator, after):
	empty = False
	try:
		first = generator.next()
	except StopIteration:
		empty = True
	if not empty:
		yield before
		yield first
		for value in generator:
			yield value
		yield after

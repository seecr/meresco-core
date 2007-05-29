from meresco.teddy import document

class XSlice:
	"""XSlice wraps around a list-like object (supporting __getitem__) to enable taking slices of this list that are generators (no copying until needed)."""
		
	def __init__(self, aList):
		self._list = aList
		
	def __len__(self):
		return len(self._list)
	
	def __getslice__(self, start, stop):
		stop = min(len(self), stop)
		for i in xrange(start, stop):
			yield self._list[i]
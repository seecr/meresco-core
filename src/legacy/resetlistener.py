class ResetListener:
	
	def __init__(self, index):
		self._index = index
	
	def notify(self, *args):
		self._index.optimize()
		self._index.reOpen()
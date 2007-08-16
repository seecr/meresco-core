class BitMatrix(object):
	"to be written in Pyrex/C completely"
	def __init__(self, numberOfDocs = None):
		self._rows = []

	def addRow(self, columnNumbers):
		self._rows.append(set(columnNumbers))
		return len(self._rows) - 1

	def combinedRowCardinalities(self, columnNumbers, maxresults = None):
		# beware the ?functionlity? of sortAndTruncateAndGetMinValueInResult !
		columns = set(columnNumbers)
		return [(nr, occ) for nr, occ in
			((nr, len(columns.intersection(row))) for nr, row in
				enumerate(self._rows)) if occ]

	def rowCadinalities(self):
		return [(nr, len(row)) for nr, row in enumerate(self._rows)]

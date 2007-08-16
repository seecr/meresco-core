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
		result = []
		for nr, row in enumerate(self._rows):
			cardinality = len(columns.intersection(row))
			if cardinality:
				result.append((nr, cardinality))
		return result

	def rowCadinalities(self):
		result = []
		for nr, row in enumerate(self._rows):
			result.append((nr, len(row)))
		return result

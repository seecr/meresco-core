## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) 2007 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2007 Stichting Kennisnet Ict op school. 
#       http://www.kennisnetictopschool.nl
#
#    This file is part of Meresco Core.
#
#    Meresco Core is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Meresco Core is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Meresco Core; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
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

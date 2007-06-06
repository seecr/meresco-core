## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) SURF Foundation. http://www.surf.nl
#    Copyright (C) Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) SURFnet. http://www.surfnet.nl
#    Copyright (C) Stichting Kennisnet Ict op school. 
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
from cq2utils.observable import Observable
from cq2utils.component import Notification

STAMP_PART = '__stamp__' # __ because purpose is internal use only!
DATESTAMP = 'datestamp'
UNIQUE = 'unique'

from time import gmtime, strftime
from amara.binderytools import bind_string
from cq2utils.uniquenumbergenerator import UniqueNumberGenerator

class StampComponent(Observable):
	
	uniqueFormat = '%019i'
	"""Since we don't work with Integer-fields, only with string-fields, some measure must be taken to garantuee lexicographical sorting works - this is done by padding 64bit zeros
	19 == int(floor(log(pow(2, 64), 10))) == len('18446744073709551616')"""
	
	def __init__(self, uniqueNumbersFilename):
		Observable.__init__(self)
		self.unique = UniqueNumberGenerator(uniqueNumbersFilename)
	
	def getTime(self):
		return strftime('%Y-%m-%dT%H:%M:%SZ', gmtime())
		#na al dat nadenken wat we hier eerder over gedaan hebben (denk aan urlcache ed.) kan ik me niet voorstellen dat het zo simpel is.
	
	def notify(self, notification):
		time = self.getTime()

		unique = self.unique.next()
		newNotification = Notification()
		newNotification.method = "add"
		newNotification.id = notification.id
		newNotification.partName = STAMP_PART
		thexml = bind_string("""<%(STAMP_PART)s xmlns:teddy="http://www.cq2.nl/teddy">
			<%(TIME_FIELD)s teddy:tokenize="false">%(time)s</%(TIME_FIELD)s>
			<%(UNIQUE_FIELD)s>%(unique)s</%(UNIQUE_FIELD)s>
		</%(STAMP_PART)s>""" % 
			{'time': time,
			'unique': self.uniqueFormat % unique,
			'STAMP_PART': STAMP_PART,
			'TIME_FIELD': DATESTAMP,
			'UNIQUE_FIELD': UNIQUE} #hmmm...
			)
		newNotification.payload = thexml.rootNode.childNodes[0]
		self.changed(newNotification)
		

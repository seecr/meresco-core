from cq2utils.observable import Observable
from cq2utils.component import Notification

STAMP_PART = '__internal__'
TIME_FIELD = 'datestamp'
UNIQUE_FIELD = 'unique'

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
			<%(TIME_FIELD)s teddy:tokenize='false'>%(time)s</%(TIME_FIELD)s>
			<%(UNIQUE_FIELD)s>%(unique)s</%(UNIQUE_FIELD)s>
		</%(STAMP_PART)s>""" % 
			{'time': time,
			'unique': self.uniqueFormat % unique,
			'STAMP_PART': STAMP_PART,
			'TIME_FIELD': TIME_FIELD,
			'UNIQUE_FIELD': UNIQUE_FIELD} #hmmm...
			)
		newNotification.payload = thexml.rootNode.childNodes[0] #TODO tokenize = false
		self.changed(newNotification)
		

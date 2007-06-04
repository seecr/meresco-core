
from unittest import TestCase
from meresco.queryserver.observers.undertaker import Undertaker
from cq2utils.component import Notification
from amara.binderytools import bind_string

class UnderTakerTest(TestCase):
	
	def setUp(self):
		self.undertaker = Undertaker()
		self.undertaker.addObserver(self)
		self.notifyCalls = []
		self.deletedParts = []
	
	def testAdd(self):
		notification = Notification('add', 'AN_ID', 'A_PARTNAME', 'A PAYLOAD (is in reality amary object)')
		self.undertaker.notify(notification)
		self.assertEquals([(notification,)], self.notifyCalls)
		self.assertEquals([('AN_ID', '__tombstone__')], self.deletedParts)
		
	def testDelete(self):
		xml = bind_string("<__tombstone__/>").__tombstone__
		notification = Notification('delete', 'AN_ID')
		self.undertaker.notify(notification)
		self.assertEquals(map(str, [
			(notification,),
			(Notification('add', 'AN_ID', '__tombstone__', xml),)]), map(str, self.notifyCalls))
		
	def notify(self, *args):
		"""self shunt"""
		self.notifyCalls.append(args)
		
	def undo(self, *args):
		pass
	
	def deletePart(self, id, partName):
		self.deletedParts.append((id, partName))

from unittest import TestCase
from meresco.queryserver.observers.setscomponent import SetsComponent
from cq2utils.component import Notification
from amara.binderytools import bind_string

class SetsComponentTest(TestCase):
	
	def setUp(self):
		self.notifications = []
	
	def testSets(self):
		notification = Notification("add", "id_1")
		notification.sets = [("one:two:three", "Three Piggies"), ( "one:two:four", "Four Chickies")]
		setsComponent = SetsComponent()
		setsComponent.addObserver(self)
		setsComponent.notify(notification)
		
		setsNotification = Notification("add", "id_1", "__sets__", bind_string("""<__sets__><set><setSpec>one:two:three</setSpec><setName>Three Piggies</setName></set><set><setSpec>one:two:four</setSpec><setName>Four Chickies</setName></set></__sets__>"""))
		
		self.assertEquals([(setsNotification, )], self.notifications)
		
	def notify(self, *args):
		self.notifications.append(args)
	
	def undo(self, *args):
		pass
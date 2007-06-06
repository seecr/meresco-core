
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
		
	def testNoSets(self):
		notification = Notification("add", "id_1")
		
		setsComponent = SetsComponent()
		setsComponent.addObserver(self)
		setsComponent.notify(notification)

		self.assertEquals([], self.notifications)
		
	def testFlattenedSets(self):
		notification = Notification("add", "id_1")
		notification.sets = [("one:two:three", "Three Piggies"), ("one:two:four", "Four Chickies")]
		setsComponent = SetsComponent(self)
		setsComponent.notify(notification)
		
		setsNotification = Notification("add", "id_1", "__sets__", bind_string("""<__sets__><set %(tokenized)s>one:two:three</set><set %(tokenized)s>one:two</set><set %(tokenized)s>one:two:four</set><set %(tokenized)s>one</set></__sets__>""" % {"tokenized": 'xmlns:teddy="http://www.cq2.nl/teddy" teddy:tokenize="false"'}).__sets__)
		
		self.assertEquals([(setsNotification, )], self.notifications)

	def testSetsDatabase(self):
		notification = Notification("add", "id_1")
		notification.sets = [("one:two:three", "Three Piggies"), ( "one:two:four", "Four Chickies")]
		setsComponent = SetsComponent(None, self)
		setsComponent.notify(notification)
		
		self.assertEquals(2, len(self.notifications))
		
		one = Notification("add", "one:two:three", "set", bind_string("""<set><setSpec>one:two:three</setSpec><setName>Three Piggies</setName></set>""").set)
		
		two = Notification("add", "one:two:four", "set", bind_string("""<set><setSpec>one:two:four</setSpec><setName>Four Chickies</setName></set>""").set)
		
		self.assertEquals((one, ), self.notifications[0])
		self.assertEquals((two, ), self.notifications[1])

	def notify(self, *args):
		self.notifications.append(args)
	
	def undo(self, *args):
		pass
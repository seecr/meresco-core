
from cq2utils.component import Component, Notification
from cq2utils.observable import Observable
from amara import binderytools


class Venturi(Component, Observable):
	"""
	Will create a new or update an existing document with a notification
	"""
	def __init__(self, venturiName, storage):
		Observable.__init__(self)
		self._storage = storage
		self._venturiName = venturiName
		
	def add(self, notification):
		unit = self._storage.getUnit(notification.id)
		newNode = notification.payload
		if unit.hasBox(self._venturiName):
			box = unit.openBox(self._venturiName)
			try:
				venturiObject = binderytools.bind_stream(box).rootNode.childNodes[0]
				existingNode = getattr(venturiObject, newNode.localName, None)
				if existingNode:
					venturiObject.xml_remove_child(existingNode)
			finally:
				box.close()
		else:
			venturiObject = binderytools.bind_string('<%s/>' % self._venturiName).rootNode.childNodes[0]
		venturiObject.xml_append(newNode)
		
		newNotification = Notification('add', notification.id, self._venturiName, venturiObject)
		self.changed(newNotification)

from cq2utils.observable import Observable
from amara import binderytools
from cq2utils.component import Notification
		
class XmlInflate(Observable):
	def notify(self, notification):
		newNotification = Notification(notification.method, notification.id, notification.partName)
		newNotification.payload = notification.payload and binderytools.bind_string(notification.payload).rootNode.childNodes[0] or None
		self.changed(newNotification)
	
	def undo(self, *args, **kwargs):
		pass

class XmlDeflate(Observable):
	#TODO (2x) testen op niet aantasten None-payloads?
	def notify(self, notification):
		newNotification = Notification(notification.method, notification.id, notification.partName)
		newNotification.payload = notification.payload and notification.payload.xml() or None
		self.changed(newNotification)
	
	def undo(self, *args, **kwargs):
		pass


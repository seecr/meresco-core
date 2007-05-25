from cq2utils.observable import Observable
from cq2utils.component import Notification
from amara.binderytools import bind_string

class Undertaker(Observable):
	
	def notify(self, notification):
		self.changed(notification)
		if notification.method == "delete":
			graveStone = Notification("add", notification.id, "__tombstone__", bind_string("<__internal__><__tombstone__>__tombstone__</__tombstone__></__internal__>").__internal__)
			self.changed(graveStone)
		if notification.method == "add":
			graveDestruction = Notification("delete", notification.id)
	
	def undo(self, *args, **kwargs):
		pass
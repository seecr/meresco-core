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

PARTS_PART = '__parts__' # __ because purpose is internal use only!
PART = 'part'

from amara.binderytools import bind_string

class PartsComponent(Observable):
	
	def __init__(self, storage, maintainedParts):
		Observable.__init__(self)
		self.maintainedParts = maintainedParts
		self._storage = storage
	
	def notify(self, notification):
		self.changed(notification)
		
		if notification.partName in self.maintainedParts:
			unit = self._storage.getUnit(notification.id)
			newNode = notification.payload
			parts = set()
			if unit.hasBox(PARTS_PART):
				box = unit.openBox(PARTS_PART)
				try:
					parts_xml = binderytools.bind_stream(box).__parts__
					for part in parts_xml:
						parts.add(str(part))
				finally:
					box.close()
			if notification.method == "add":
				parts.add(notification.partName)
			elif notification.method == "delete":
				parts.remove(notification.partName)
			
			thexml = "<__parts__>%s</__parts__>"  % "".join(map(
				lambda s: "<part>%s</part>" % s,
				parts))
			
			newNotification = Notification("add", notification.id, PARTS_PART, bind_string(thexml).__parts__)
			self.changed(newNotification)
## begin license ##
#
#    Teddy is the name for Seek You Too's Search Appliance.
#    Copyright (C) 2006 Stichting SURF. http://www.surf.nl
#    Copyright (C) 2006-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of Teddy.
#
#    Teddy is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Teddy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Teddy; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
from cq2utils.component import Component

class StorageComponent(Component):
	def __init__(self, aStorage):
		self._storage = aStorage

	def add(self, notification):
		unit = self._storage.getUnit(notification.id)
		stream = unit.openBox(notification.partName, 'w')
		try:
			stream.write(notification.payload)
		finally:
			stream.close()
			
	def isAvailable(self, id, partName):
		"""returns (hasId, hasPartName)"""
		if self._storage.hasUnit(id):
			unit = self._storage.getUnit(id) #caching optional
			return True, unit.hasBox(partName)
		return False, False
	
	def write(self, sink, id, partName):
		unit = self._storage.getUnit(id) #caching optional
		stream = unit.openBox(partName)
		try:
			sink.write(stream.read())
		finally:
			stream.close()
			
	def undo(self, *args, **kwargs):
		pass
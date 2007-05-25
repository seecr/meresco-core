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
from amara import binderytools
from xml.sax import SAXParseException

class IndexComponent(Component):
	def __init__(self, anIndex):
		self._index = anIndex
		self._latestId = None
		
	def delete(self, notification):
		self._index.deleteID(notification.id)
		self._latestId = None
			
	def undo(self, *args, **kwargs):
		if self._latestId:
			self._index.deleteID(self._latestId)
		self._latestId = None
	
	def add(self, notification):
		self._latestId = None
		self._index.deleteID(notification.id)
		self._index.addToIndex(notification.document)
		self._latestId = notification.id
			
	def listRecords(self, continueAt = '0'):
		#TODO test this method
		#TODO ik (KVS) vermoed dat bij een lege index het sorteren tot problemen leidt (dwz excepties)
		query = '__internal__.unique:{%s TO A} NOT __internal__.__tombstone__:__tombstone__' % continueAt
		return self._index.createQuery(query, aCount = float('Infinity'), sortBy = '__internal__.unique').perform()
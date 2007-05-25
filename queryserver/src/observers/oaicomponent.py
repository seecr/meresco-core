## begin license ##
#
#    QueryServer is a framework for handling search queries.
#    Copyright (C) 2005-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of QueryServer.
#
#    QueryServer is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    QueryServer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with QueryServer; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from oai.oaitool import OaiVerb
from oaiidentify import OaiIdentify
from oaigetrecord import OaiGetRecord
from oailistrecords import OaiListRecords
from oaisink import OaiSink

from cq2utils.observable import Observable

class OaiComponent(Observable):
	
	def __init__(self):
		Observable.__init__(self)
		self._privateTree = Observable()
		for aClass in [OaiIdentify, OaiGetRecord, OaiListRecords, OaiSink]:
			branch = aClass()
			branch.changed = self.changed
			branch.any = self.any
			branch.all = self.all
			self._privateTree.addObserver(branch)
	
	def notify(self, webRequest):
		return self._privateTree.process(webRequest)
		
	def undo(self, *args, **kwargs):
		"""Ignored"""
		pass
	

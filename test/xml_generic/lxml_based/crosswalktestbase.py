## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) 2007 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2007 Stichting Kennisnet Ict op school. 
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
from unittest import TestCase

from lxml.etree import parse, tostring, XMLParser
from meresco.components import Crosswalk
from difflib import unified_diff

def readRecord(name):
	return open('data/' + name).read()


class CrosswalkTestBase(TestCase):

	def setUp(self):
		class Interceptor:
			def notify(inner, notification): self.message = notification
			def undo(*args): pass
		self.plugin = CrosswalkComponent()
		self.plugin.addObserver(Interceptor())

	def assertRecord(self, id, name='LOMv1.0'):
		inputRecord = readRecord('%s.xml' % id)
		sollRecord = tostring(parse(open('data/%s.%s.xml' % (id, name)), XMLParser(remove_blank_text=True)), pretty_print = True)
		notification = Notification(method = 'add', id=None, partName='metadata', payload = inputRecord)
		try:
			self.plugin.notify(notification)
		except Exception, e:
			if hasattr(self, 'message'):
				for nr, line in enumerate(self.message.payload.split('\n')): print nr, line
			raise
		self.assertTrue(hasattr(self, 'message'))
		diffs = list(unified_diff(self.message.payload.split('\n'), sollRecord.split('\n'), fromfile='ist', tofile='soll', lineterm=''))
		self.assertFalse(diffs, '\n' + '\n'.join(diffs))


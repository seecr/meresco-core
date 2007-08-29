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


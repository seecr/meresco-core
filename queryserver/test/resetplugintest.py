
from cq2utils.cq2testcase import CQ2TestCase
from cq2utils.calltrace import CallTrace

from plugins.resetplugin import ResetPlugin, registerOn
from cStringIO import StringIO

class ResetPluginTest(CQ2TestCase):
	def setUp(self):
		CQ2TestCase.setUp(self)
		self.stream = StringIO()
		self.request = CallTrace('Request')
		client = CallTrace('client')
		self.request.client = client
		client.host = '127.0.0.1'
		self.request.write = self.stream.write
		self.request.args = {}
		self.request.database = 'database'
		self.searchInterface = CallTrace('SearchInterface')
		self.plugin = ResetPlugin(self.request, self.searchInterface)
	
	def testRegistry(self):
		registry = CallTrace('PluginRegistry')
		registerOn(registry)
		self.assertEquals(1, len(registry.calledMethods))
		self.assertEquals("registerByCommand('reset', <class plugins.resetplugin.ResetPlugin>)", str(registry.calledMethods[0]))
		
	def testReset(self):
		self.plugin.process()
		self.assertEquals(1, len(self.searchInterface.calledMethods))
		self.assertEquals("reset()", str(self.searchInterface.calledMethods[0]))
		self.assertEqualsWS('Done', self.stream.getvalue())
		
	def testExternalReset(self):
		self.request.client.host = '1.1.1.1'
		self.plugin.process()
		self.assertEquals(0, len(self.searchInterface.calledMethods))
		self.assertEqualsWS('Not authorized', self.stream.getvalue())
		

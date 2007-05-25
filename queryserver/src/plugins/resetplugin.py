
from queryplugin import QueryPlugin

class ResetPlugin(QueryPlugin):
	def initialize(self):
		self.contentType = 'text/plain'
		
	def process(self):
		if str(self._request.client.host) == '127.0.0.1':
			self.searchInterface.reset()
			self.write('Done')
		else:
			self.write('Not authorized')


def registerOn(pluginRegistry):
	pluginRegistry.registerByCommand('reset', ResetPlugin)

import sys
import traceback
import time
from queryserver.pluginregistry import PluginRegistry
from teddy.teddyinterfaceconstructor import construct as constructSearchInterfaces

def log(aString):
	try:
		sys.stdout.write(str(aString)+"\n")
		sys.stdout.flush()
	except:
		pass


class PluginAdapter(object):
	def __init__(self, configuration):
		self.configuration = configuration
	
		self.pluginRegistry = PluginRegistry(configuration)
		self.pluginRegistry.loadPlugins()
	
		self.searchInterfaces = constructSearchInterfaces(configuration)

	def getenv(self, key):
		return self.configuration.get(key,  None)
	
	def undo(self, *args, **kwargs):
		pass
	

	def notify(self, aRequest):
		ignored, database, command, tail = (aRequest.path + '//').split('/',3)
		if database not in self.searchInterfaces.keys():
			return
		if not self.pluginRegistry.supportedCommand(command):
			return
		try:
			#assemble request
			aRequest.database = database
			aRequest.command = command
			aRequest.serverurl = 'http://%s:%s' % (self.getenv('server.host'), self.getenv('server.port'))
			aRequest.getenv = self.getenv
			aRequest.log = self.log
			aRequest.logException = self.logException

			
			plugin = self.pluginRegistry.create(command, aRequest, self.searchInterfaces[database])
			plugin.process()
		except Exception, e:
			self.logException()
			aRequest.setResponseCode(e.errorCode)
			aRequest.setHeader('content-type', e.contentType)
			aRequest.write(str(e))
		
		
	def logException(self):
		self.log(traceback.format_exc())
		
	def log(self, something):
		log(str(something))

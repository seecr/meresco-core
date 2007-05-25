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

import sys
from glob import glob
from plugins.queryplugin import PluginException
from os.path import basename

class NoSuchPluginException(PluginException):
	def __init__(self, command):
		PluginException.__init__(self, '<?xml version="1.0"?><error>Command "%(command)s" not found.</error>' % locals())

class PluginRegistry:
	def __init__(self, configuration):
		self._configuration = configuration
		self._factories = []
		self._registeredCommands = []

	def registerByCommand(self, command, factoryProduct):
		def typeFactory(commandInner, *args):
			if commandInner == command:
				return factoryProduct(*args)
			return None
		self._factories.append(typeFactory)
		self._registeredCommands.append(command)
		return typeFactory
	
	def create(self, command, *args):
		for factory in self._factories:
			component = factory(command, *args)
			if component:
				return component
		raise NoSuchPluginException(command)
	
	def loadPlugins(self):
		directory = self._configuration['server.pluginpath']
		sys.path.append(directory)
		for pyfile in glob('%s/*.py' % directory):
			if not pyfile.endswith('__init__.py'):
				filename = basename(pyfile[:-3])
				module = self._loadModule(filename)
				if hasattr(module, 'registerOn'):
					module.registerOn(self)
					
	def getenv(self, key):
		return self._configuration.get(key, None)

	def size(self):
		return len(self._factories)
	
	def supportedCommand(self, command):
		return command in self._registeredCommands

	def _loadModule(self, filename):
		return __import__(filename)

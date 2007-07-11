## begin license ##
#
#    "CQ2 Utils" (cq2utils) is a package with a wide range of valuable tools.
#    Copyright (C) 2005, 2006 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of "CQ2 Utils".
#
#    "CQ2 Utils" is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    "CQ2 Utils" is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with "CQ2 Utils"; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from observable import Observable
from twisted.web import http
from twisted.internet import reactor
from sys import stdout, stderr
import traceback

class ObservableServer(Observable):
	def __init__(self, port):
		Observable.__init__(self)
		self.port = port
		
	def log(self, something):
		print >> stdout, something
		stdout.flush()
		
	def logError(self):
		print >> stderr, traceback.format_exc()
		stderr.flush()
	
	def run(self):
		class WebRequest(http.Request):
			def log(inner, something):
				self.log(something)
			def __str__(inner):
				return '\t'.join([inner.client.host, inner.method, inner.uri])
			def process(inner):
				try:
					self.changed(inner)
				except:
					self.logError()
				inner.finish()
		class WebHTTPChannel(http.HTTPChannel):
			requestFactory = WebRequest
		class Factory(http.HTTPFactory):
			protocol = WebHTTPChannel
		factory = Factory()
		reactor.listenTCP(self.port, factory)
		self.log("Ready to rumble at %d\n" % self.port)
		reactor.run()

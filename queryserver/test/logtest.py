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
from unittest import TestCase

from plugins.log import Log
from cStringIO import StringIO
from cq2utils.calltrace import CallTrace

class LogTest(TestCase):
	
	def testLogging(self):
		stream = StringIO()
		log = Log(stream)
		
		webRequest = CallTrace('WebRequest')
		webRequest.method = 'GET'
		webRequest.uri = '/path/to/server?key=value'
		client = CallTrace('IPv4Address')
		client.host = "192.168.1.2"
		webRequest.client = client
		log.notify(webRequest)
		
		date, ipaddress, method, uri = stream.getvalue().strip().split('\t')
		self.assertEquals("192.168.1.2", ipaddress)
		self.assertEquals('GET', method)
		self.assertEquals('/path/to/server?key=value', uri)
		

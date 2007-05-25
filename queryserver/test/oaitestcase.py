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

from cq2utils.cq2testcase import CQ2TestCase

from cq2utils.calltrace import CallTrace
from cq2utils.observable import Observable
from cStringIO import StringIO
from observers.oai.oaivalidator import assertValidString

from observers.oaicomponent import OaiComponent
from observers.oaisink import OaiSink

class OaiTestCase(CQ2TestCase):
	
	def setUp(self):
		CQ2TestCase.setUp(self)
		self.observable = Observable()
		self.subject = self.getSubject()
		self.subject.getTime = lambda : '2007-02-07T00:00:00Z'
		self.observable.addObserver(self.subject)
		self.request = CallTrace('Request')
		#self.request.serverurl = 'http://:9000'
		self.request.path = '/path/to/oai'
		self.request.getRequestHostname = lambda: 'server'
		class Host:
			def __init__(self):
				self.port = '9000'
		self.request.getHost = lambda: Host()
		self.stream = StringIO()
		self.request.write = self.stream.write
		
	def testNotMyVerb(self):
		"""All verbs are observers and should only react to their own verb. This is not true for the sink and the umbrella OaiComponent"""
		if self.subject.__class__ in [OaiComponent, OaiSink]:
			return
		self.request.args = {'verb': ['NotMyVerb']}
		self.observable.changed(self.request)
		self.assertEquals('', self.stream.getvalue())
		
	def assertBadArgument(self, arguments, additionalMessage = ''):
		#NOTE: this method can be used only once per test (not very pretty, but not priority now (20/04/2007 - KVS)
		
		self.request.args = arguments
		self.observable.changed(self.request)
		self.assertEquals("setHeader('content-type', 'text/xml; charset=utf-8')",  str(self.request.calledMethods[0]))
		result = self.stream.getvalue()
		self.assertTrue(result.find("""<error code="badArgument">""") > -1)
		self.assertTrue(result.find(additionalMessage) > -1, 'Expected "%s" in "%s"' %(additionalMessage, result))
		assertValidString(result)
		
	OAIPMH = """<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/
         http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
<responseDate>2007-02-07T00:00:00Z</responseDate>
%s
</OAI-PMH>"""
	

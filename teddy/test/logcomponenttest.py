## begin license ##
#
#    Teddy is the name for Seek You Too's Search Appliance.
#    Copyright (C) 2006 Stichting SURF. http://www.surf.nl
#    Copyright (C) 2006-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of Teddy.
#
#    Teddy is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Teddy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Teddy; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from cq2utils.cq2testcase import CQ2TestCase

from logcomponent import LogComponent
from cq2utils.component import Notification
from cq2utils.observable import Observable
from cq2utils.calltrace import CallTrace

class LogComponentTest(CQ2TestCase):
	
	def testLog(self):
		notification = Notification("method", "anId", "partName", 'payload')
		
		observable = Observable()
		component = LogComponent(self.tempfile)
		observable.addObserver(component)
		
		observable.changed(notification)
		
		oneline = open(self.tempfile).read().strip()
		time, message = oneline.split('\t')
		self.assertEquals("notify: %s" % str(notification), message)
		self.assertTrue(float(time))
		
	def testLogException(self):
		faultyObserver = CallTrace('Faulty Observer')
		faultyObserver.exceptions['notify'] = Exception('Something bad happened')
		
		notification = Notification("method", "anId", "partName", 'payload')
		
		observable = Observable()
		component = LogComponent(self.tempfile)
		observable.addObserver(component)
		observable.addObserver(faultyObserver)
		
		try:
			observable.changed(notification)
			self.fail()
		except Exception, e:
			self.assertEquals('Something bad happened', str(e))
		
		lines = map(str.strip, open(self.tempfile).readlines())
		self.assertTrue(len(lines) > 2)
		time, message = lines[-1].split('\t')
		self.assertEquals("undo" , message)
		self.assertTrue(float(time))

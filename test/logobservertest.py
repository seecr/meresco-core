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
from unittest import TestCase

from meresco.components.logobserver import LogObserver
from cStringIO import StringIO
from cq2utils.calltrace import CallTrace
from meresco.framework.observable import Observable

class LogObserverTest(TestCase):
	
	def testLogging(self):
		stream = StringIO()
		log = LogObserver(stream)
		
		class AnArgument:
			def __str__(self):
				return 'Looking for an argument.'
		argument = AnArgument()		
		log.notify('one', argument, 'three')
		
		time, line = stream.getvalue().split('\t',1)
		self.assertEquals('one\tLooking for an argument.\tthree\n', line)
		
	def testLoggingBySubclassing(self):
		stream = StringIO()
		arguments = []
		class MyLogObserver(LogObserver):
			def toString(self, *args):
				arguments.append(args)
				return 'toString'
		log = MyLogObserver(stream)
		
		log.notify('one', 'two')
		
		time, line = stream.getvalue().split('\t',1)
		self.assertEquals('toString\n', line)
		self.assertEquals([('one','two')], arguments)

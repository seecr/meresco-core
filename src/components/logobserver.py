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

from time import strftime, gmtime
from sys import stdout, exc_info
from traceback import format_exception

class LogObserver(object):
	def __init__(self, stream = stdout, printtime = True):
		self._stream = stream
		self.write = self._stream.write
		self.flush = self._stream.flush
		self._printtime = printtime
		
	def _write(self, aString):
		if self._printtime:
			self.write( '%s\t' % strftime("%Y-%m-%dT%H:%M:%SZ", gmtime()))
		self.write('%s\n' % aString)
		self.flush()
		
	def notify(self, *args):
		self._write(self.toString(*args))
		
	def toString(self, *args):
		return '\t'.join(map(str, args))

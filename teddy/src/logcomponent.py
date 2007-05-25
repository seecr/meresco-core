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

from time import time

from sys import exc_info
from traceback import format_exception

class LogComponent:
	def __init__(self, logfile):
		self._logfile = logfile
		
	def _write(self, line):
		f = open(self._logfile, 'a')
		try:
			f.write(str(time()))
			f.write('\t')
			f.write(line)
			f.write('\n')
		finally:
			f.close()
		
	def notify(self, *args):
		self._write("notify: " + ', '.join(map(str, args)))
		
	def undo(self, *args, **kwargs):
		info = exc_info()
		lines = map(str.strip, format_exception(*info))
		for line in lines:
			for subline in line.split('\n'):
				self._write(subline)

		self._write("undo")
	

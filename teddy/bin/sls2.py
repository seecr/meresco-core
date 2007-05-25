#!/usr/bin/env python
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

from storage import hex
from os.path import basename, dirname, isfile

while True:
  try:
    i = raw_input()
  except EOFError:
    break

  if isfile(i):
    filename = basename(i)
    try:
      decoded = '.'.join(map(lambda x:hex.hexStringToString(x), filename.split('.')))
      print "%s/%s (%s)" % (dirname(i), decoded, filename)      
    except ValueError:
      print i
  else:
    print i

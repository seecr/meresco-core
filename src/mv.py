#!/usr/bin/env python
## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) SURF Foundation. http://www.surf.nl
#    Copyright (C) Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) SURFnet. http://www.surfnet.nl
#    Copyright (C) Stichting Kennisnet Ict op school. 
#       http://www.kennisnetictopschool.nl
#
#    This file is part of Meresco Core.
#
#    Meresco Core is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Meresco Core is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Meresco Core; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

def toClass(s):
	s.index("./") #check
	s = s[2:]
	xxx = s.find(".")
	if xxx > -1:
		s = s[:xxx]
	s = s.replace("/", ".")
	return s

import sys

l = sys.stdin.readlines()
l = [s.strip().split(',') for s in l]

for x in l:
	if len(x) == 2:
	
		if x[1] == "KILL":
			print "svn rm", x[0]
		else:
			print "svn mv %s %s" % (x[0], x[1])
			blaat = [toClass(s) for s in x]
			print "find -name '*.py' | grep -v svn | grep trunk | xargs ~/scripts/replace.py %s %s" % (blaat[0], blaat[1])
			
	else:
		if ",".join(x):
			raise Exception("Malformedline %s" % "".join(x))

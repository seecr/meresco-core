#!/usr/bin/env python

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

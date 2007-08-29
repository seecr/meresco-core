## begin license ##
#
#    LOREnet is a tool for sharing knowledge within and beyond the walls of
#    your own school or university.
#    Copyright (C) 2006-2007 Stichting SURF. http://www.surf.nl
#    Copyright (C) 2006-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of Meresco.
#
#    LOREnet is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    LOREnet is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with LOREnet; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
from StringIO import StringIO
from lxml.etree import parse, XMLParser
from cq2utils.xmlutils.xmlrewrite import XMLRewrite
from glob import glob
from os.path import basename, dirname

from meresco.framework import Observable

extension = '.rules'

def rewriteRules(pattern, replacement, rules):
	return [rewrite(pattern, replacement, rule) for rule in rules]

def rewrite(pattern, replacement, rules):
	if type(rules) == str:
		return rules.replace(pattern, replacement)
	if type(rules) == tuple:
		return tuple(rewrite(pattern, replacement, rule) for rule in  rules)
	return rules

class Crosswalk(Observable):

	def __init__(self, rulesDir=dirname(__file__)):
		Observable.__init__(self)
		self.ruleSet = {}
		self.rulesDir = rulesDir
		if rulesDir:
			for fileName in glob(rulesDir + '/*' + extension):
				args = {}
				self.readConfig(basename(fileName[:-len(extension)]), args)
				self.ruleSet[args['inputNamespace']] = args
				del args['inputNamespace']

	def readConfig(self, ruleSetName, localsDict):
		globs = {'extend': lambda name: self.readConfig(name, localsDict), 'rewriteRules': rewriteRules}
		execfile(self.rulesDir + '/' + ruleSetName + extension, globs, localsDict)


	def notify(self, notification):
		if notification.method != 'add': return
		if notification.partName != 'metadata': return
		tree = parse(StringIO(notification.payload), XMLParser(remove_blank_text=True))
		root = tree.getroot()
		namespaceURI = root.nsmap[root.prefix]
		rewrite = XMLRewrite(tree, **self.ruleSet[namespaceURI])
		rewrite.applyRules()
		self.changed(Notification(notification.method, notification.id, 'LOMv1.0', rewrite.toString()))

	def __str__(self):
		return 'CrosswalkComponent'

## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
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
from StringIO import StringIO
from lxml.etree import parse, XMLParser, _ElementTree
from cq2utils.xmlutils.xmlrewrite import XMLRewrite
from cq2utils.xmlutils import findNamespaces
from glob import glob
from os.path import basename, dirname, abspath, join

from meresco.core import Observable

EXTENSION = '.rules'

def rewriteRules(pattern, replacement, rules):
    return [rewrite(pattern, replacement, rule) for rule in rules]

def rewrite(pattern, replacement, rules):
    if type(rules) == str:
        return rules.replace(pattern, replacement)
    if type(rules) == tuple:
        return tuple(rewrite(pattern, replacement, rule) for rule in  rules)
    return rules

class Crosswalk(Observable):
    def __init__(self, argumentKeyword = None, rulesDir=join(abspath(dirname(__file__)), 'rules'), extraGlobals={}):
        assert argumentKeyword == None, 'Crosswalk converts any argument that looks like an Lxml ElementTree, usage of argumentKeyword is forbidden.'

        Observable.__init__(self)
        self.ruleSet = {}
        self.rulesDir = rulesDir
        self._globs = {}
        self._globs.update(extraGlobals)
        self._globs['rewriteRules']= rewriteRules

        if rulesDir:
            for fileName in glob(rulesDir + '/*' + EXTENSION):
                args = {}
                self.readConfig(basename(fileName[:-len(EXTENSION)]), args)
                self.ruleSet[args['inputNamespace']] = args
                del args['inputNamespace']

    def readConfig(self, ruleSetName, localsDict):
        self._globs['extend']= lambda name: self.readConfig(name, localsDict)
        execfile(self.rulesDir + '/' + ruleSetName + EXTENSION, self._globs, localsDict)

    def _detectAndConvert(self, anObject):
        if type(anObject) == _ElementTree:
            return self.convert(anObject)
        return anObject

    def unknown(self, method, *args, **kwargs):
        newArgs = [self._detectAndConvert(arg) for arg in args]
        newKwargs = dict((key, self._detectAndConvert(value)) for key, value in kwargs.items())
        return self.all.unknown(method, *newArgs, **newKwargs)

    def convert(self, lxmlNode):
        nsmap = findNamespaces(lxmlNode)
        if type(lxmlNode) == _ElementTree:
            prefix = lxmlNode.getroot().prefix
        else:
            prefix = lxmlNode.prefix
        if not prefix in nsmap:
            raise Exception("Prefix '%s' not found in rules, available namespaces: %s" % (prefix, nsmap.keys()))
        namespaceURI = nsmap[prefix]
        rewrite = XMLRewrite(lxmlNode, **self.ruleSet[namespaceURI])
        rewrite.applyRules()
        return rewrite.asLxml()

    def __str__(self):
        return 'CrosswalkComponent'

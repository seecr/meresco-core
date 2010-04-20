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

from meresco.core import Observable
from warnings import warn
from lxml.etree import _Element

def removeNamespace(tagName):
    return '}' in tagName and tagName.split('}')[1] or tagName


class Xml2Fields(Observable):

    def add(self, id, partName, lxmlNode):
        """deprecated"""
        self.addXml(lxmlNode)

    def addXml(self, lxmlNode):
        if hasattr(lxmlNode, 'getroot'):
            lxmlNode = lxmlNode.getroot()
        return self._fillDict(lxmlNode, '')

    def _fillDict(self, aNode, parentName):
        if type(aNode) != _Element:
            return

        if parentName:
            parentName += '.'
        localName = removeNamespace(aNode.tag)
        fieldname = parentName + localName
        value = aNode.text
        if value and value.strip():
            self.do.addField(name=fieldname, value=value)
        for child in aNode.getchildren():
            self._fillDict(child, fieldname)


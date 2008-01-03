## begin license ##
#
#    Meresco Core is an open-source library containing components to build 
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school. 
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
from amara import binderytools
from amara.bindery import is_element
from meresco.framework.observable import Observable
from meresco.components.dictionary import DocumentDict

class Xml2Dict(Observable):

    def add(self, id, partName, amaraXmlNode):
        dd = DocumentDict()
        self._fillDict(amaraXmlNode, dd, '')
        return self.all.addDocumentDict(id, partName, dd)

    def _fillDict(self, aNode, dd, parentName):
        if parentName:
            parentName += '.'
        tagname = parentName + str(aNode.localName)
        value = aNode.xml_child_text
        if str(value).strip():
            dd.add(tagname, str(value))

        for child in filter(is_element, aNode.childNodes):
            self._fillDict(child, dd, tagname)

    def unknown(self, *args, **kwargs):
        return self.all.unknown(*args, ** kwargs)
        

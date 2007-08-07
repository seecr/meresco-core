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

from meresco.components.lucene.document import Document
from amara import binderytools
from amara.bindery import is_element
from meresco.framework.observable import Observable

TEDDY_NS = "http://www.cq2.nl/teddy"

class Xml2Document(Observable):
    
    def unknown(self, methodName, *args):
        self.do.unknown(methodName, *args)
    
    def add(self, id, partName, amaraXmlNode):
        self.do.add(id, partName, self._create(id, amaraXmlNode))
    
    def _create(self, documentId, topNode):
        doc = Document(documentId)
        self._addToDocument(doc, topNode, '')
        return doc
        
    def _addToDocument(self, doc, aNode, parentName):
        if parentName:
            parentName += '.'
        for child in filter(is_element, aNode.childNodes):
            self._indexChild(child, doc, parentName)
    
    def _indexChild(self, child, doc, parentName):
        tagname = parentName + str(child.localName)
        value = child.xml_child_text
        tokenize = True
        skip = False
        for xpathAttribute in child.xpathAttributes:
            if xpathAttribute.namespaceURI == TEDDY_NS:
                if xpathAttribute.localName == 'tokenize':
                    tokenize = str(xpathAttribute.value).lower() != 'false'
                if xpathAttribute.localName == 'skip':
                    skip = str(xpathAttribute.value).lower() == 'true'
                    tagname = ''
        if not skip and str(value).strip():
            doc.addIndexedField(tagname, str(value), tokenize)
        self._addToDocument(doc, child, tagname)

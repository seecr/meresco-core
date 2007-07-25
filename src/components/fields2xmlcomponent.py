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


from meresco.framework.observable import Observable
from cq2utils.component import Component, Notification
from amara import binderytools, create_document
from xml2document import TEDDY_NS

class Fields2XmlComponent(Component, Observable):
    def __init__(self):
        Observable.__init__(self)
        
    def add(self, id, partName, someString):
        if partName != 'fields':
            return
        
        originalXml = binderytools.bind_string(someString)
        root = self._fields2Xml(originalXml)
        
        self.do.add(id, 'xmlfields', root.childNodes[0])

    def unknown(self, methodName, *args):
        self.do.unknown(methodName, *args)
        
    def _fields2Xml(self, originalXml):
        root = create_document(u'xmlfields', attributes={(u'teddy:skip', unicode(TEDDY_NS)): u'true'})
        
        for field in originalXml.fields.field:
            fieldname = None
            tokenizeAttr = None
            for attribute in field.xpathAttributes:
                if attribute.localName == 'name':
                    if ':' in attribute.value:
                        continue
                    fieldname = attribute.value
                if attribute.localName == 'tokenize':
                    tokenizeAttr = {(u'teddy:tokenize', unicode(TEDDY_NS)): attribute.value}
            if fieldname:
                newfield = root.xml_create_element(fieldname, 
                    content=unicode(field), 
                    attributes=tokenizeAttr)
                root.xmlfields.xml_append(newfield)
                
        return root

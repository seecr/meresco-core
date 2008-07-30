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
from meresco.framework.observable import Observable
from meresco.components.oai.xml2document import TEDDY_NS

from amara.bindery import is_element

TOKEN = '__untokenized__'

class DrilldownRequestFieldnameMap(Observable):
    def __init__(self, lookup, reverse):
        Observable.__init__(self)
        self.lookup = lookup
        self.reverse = reverse

    def drilldown(self, docNumbers, fieldsAndMaximums):
        translatedFields = ((self.lookup(field), maximum)
            for (field, maximum) in fieldsAndMaximums)
        drilldownResults = self.any.drilldown(docNumbers, translatedFields)
        return [(self.reverse(field), termCounts)
            for field, termCounts in drilldownResults]

class DrilldownRequestFieldFilter(DrilldownRequestFieldnameMap):
    def __init__(self):
        DrilldownRequestFieldnameMap.__init__(self,
            lambda field: field + TOKEN,
            lambda field: field[:-len(TOKEN)])

class DrilldownUpdateFieldFilter(Observable):
    def __init__(self, listOfFields):
        Observable.__init__(self)
        self._drilldownFields = listOfFields

    def fieldsForField(self, documentField):
        """Newstyle"""
        from academicopen.documentdict import DocumentField
        if documentField.key in self._drilldownFields:
            yield DocumentField(documentField.key + TOKEN, documentField.value, tokenize=False)

    def add(self, id, partName, amaraXmlNode):
        for field in self._drilldownFields:
            node = self._findNode(amaraXmlNode, field)
            if node:
                newfield = amaraXmlNode.xml_create_element(node.nodeName + TOKEN,
                    content=unicode(node),
                    ns=node.namespaceURI,
                    attributes={(u'teddy:tokenize', unicode(TEDDY_NS)): u'false'})
                node.parentNode.xml_append(newfield)
        self.do.add(id, partName, amaraXmlNode)

    def unknown(self, message, *args, **kwargs):
        self.do.unknown(message, *args, **kwargs)

    def _findNode(self, node, nodeName):
        chunks = nodeName.split('.')
        localName = chunks[0]
        if node.localName != localName:
            return None
        if len(chunks) == 1:
            return node
        else:
            remainder = '.'.join(chunks[1:])
            if remainder:
                for child in filter(lambda x:is_element(x), node.childNodes):
                    result = self._findNode(child, remainder)
                    if result:
                        return result

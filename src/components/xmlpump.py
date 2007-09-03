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
from amara import binderytools
from lxml.etree import parse, _ElementTree, tostring
from cStringIO import StringIO

class XmlInflate(Observable):

    def add(self, id, partName, xmlString):
        xml = binderytools.bind_string(xmlString)
        return self.all.add(id, partName, xml.rootNode.childNodes[0])

    def unknown(self, *args, **kwargs):
        return self.all.unknown(*args, **kwargs)

class XmlDeflate(Observable):

    def add(self, id, partName, amaraXmlNode, *args, **kwargs):
        return self.all.add(id, partName, amaraXmlNode.xml())

    def unknown(self, *args, **kwargs):
        return self.all.unknown(*args, **kwargs)

class XmlPrintLxml(Observable):
    def printXml(self, node):
        if type(node) == _ElementTree:
            return tostring(node, pretty_print = True)
        return node

    def unknown(self, msg, *args, **kwargs):
        newArgs = [self.printXml(arg) for arg in args]
        newKwargs = dict((key, self.printXml(value)) for key, value in kwargs.items())
        return self.all.unknown(msg, *newArgs, **newKwargs)

class Amara2Lxml(Observable):

    def amara2lxml(self, something):
        if 'amara.bindery.' in str(type(something)):
            return parse(StringIO(something.xml()))
        return something

    def unknown(self, msg, *args, **kwargs):
        newArgs = [self.amara2lxml(arg) for arg in args]
        newKwargs = dict((key, self.amara2lxml(value)) for key, value in kwargs.items())
        return self.all.unknown(msg, *newArgs, **newKwargs)

class Lxml2Amara(Observable):
    def lxml2amara(self, arg):
        if type(arg) == _ElementTree:
            arg = binderytools.bind_string(tostring(arg))
        return arg

    def unknown(self, msg, *args, **kwargs):
        newArgs = [self.lxml2amara(arg) for arg in args]
        newKwargs = dict((key, self.lxml2amara(value)) for key, value in kwargs.items())
        return self.all.unknown(msg, *newArgs, **newKwargs)

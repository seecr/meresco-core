## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) 2007 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2007 Stichting Kennisnet Ict op school. 
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
from amara.binderytools import bind_string
from amara.bindery import is_element
from lxml.etree import parse, _ElementTree, tostring
from cStringIO import StringIO

class Converter(Observable):
    def unknown(self, msg, *args, **kwargs):
        newArgs = [self._detectAndConvert(arg) for arg in args]
        newKwargs = dict((key, self._detectAndConvert(value)) for key, value in kwargs.items())
        return self.all.unknown(msg, *newArgs, **newKwargs)

    def _detectAndConvert(self, anObject):
        raise NotImplementedError()

class XmlParseAmara(Converter):
    def _detectAndConvert(self, anObject):
        if str == type(anObject) and anObject.strip().startswith('<') and anObject.strip().endswith('>'):
            return bind_string(anObject).childNodes[0]
        return anObject

class XmlPrintAmara(Converter):
    def _detectAndConvert(self, anObject):
        if is_element(anObject):
            return anObject.xml()
        return anObject

class XmlParseLxml(Converter):
    def _detectAndConvert(self, anObject):
        if str == type(anObject) and anObject.strip().startswith('<') and anObject.strip().endswith('>'):
            return parse(StringIO(anObject))
        return anObject

class XmlPrintLxml(Converter):
    def _detectAndConvert(self, node):
        if type(node) == _ElementTree:
            return tostring(node, pretty_print = True)
        return node

class Amara2Lxml(Converter):
    def _detectAndConvert(self, something):
        if is_element(something):
            return parse(StringIO(something.xml()))
        return something

class Lxml2Amara(Converter):
    def _detectAndConvert(self, arg):
        if type(arg) == _ElementTree:
            arg = bind_string(tostring(arg)).childNodes[0]
        return arg

# backwards compatible
XmlInflate = XmlParseAmara
XmlDeflate = XmlPrintAmara
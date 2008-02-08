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
from unittest import TestCase
from cq2utils.calltrace import CallTrace

from meresco.framework.observable import Observable

from meresco.components.dictionary import Xml2Dict, DocumentDict

from amara import binderytools

class Xml2DictTest(TestCase):
    def testOneField(self):
        xml2Dict = Xml2Dict()
        observer = CallTrace('Observer')
        xml2Dict.addObserver(observer)
        observable = Observable()
        observable.addObserver(xml2Dict)

        observable.do.add('id','partName', binderytools.bind_string('<fields><tag>value</tag></fields>').fields)

        self.assertEquals('addDocumentDict', observer.calledMethods[0].name)
        self.assertEquals(2, len(observer.calledMethods[0].args))
        self.assertEquals('id', observer.calledMethods[0].args[0])
        documentDict = observer.calledMethods[0].args[1]
        self.assertEquals(1, len(documentDict.get('fields.tag')))
        self.assertEquals('value', documentDict.get('fields.tag')[0].value)


    def testMultiLevel(self):
        documentDict = DocumentDict()
        xml2dict = Xml2Dict()

        node = binderytools.bind_string("""<lom>
            <general>
                <title>The title</title>
            </general>
        </lom>""").lom
        xml2dict._fillDict(node, documentDict, '')
        self.assertEquals('The title', documentDict.get('lom.general.title')[0].value)

    def testMultipleValuesForField(self):
        documentDict = DocumentDict()
        xml2dict = Xml2Dict()

        node = binderytools.bind_string("""<tag>
            <name>Name One</name>
            <name>Name Two</name>
        </tag>""").tag
        xml2dict._fillDict(node, documentDict, '')
        self.assertEquals(['Name One', 'Name Two'], [field.value for field in documentDict.get('tag.name')])

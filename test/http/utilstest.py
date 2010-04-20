# -*- coding: utf-8 -*-
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
import meresco.components.http.utils as utils
from unittest import TestCase
from weightless import compose

class UtilsTest(TestCase):
    def testInsertHeader(self):

        def handleRequest(*args, **kwargs):
            yield  utils.okHtml
            yield '<ht'
            yield 'ml/>'

        newHeader = 'Set-Cookie: session=dummySessionId1234; path=/'
        result = ''.join(utils.insertHeader(handleRequest(), newHeader))
        header, body = result.split(utils.CRLF*2, 1)
        self.assertEquals('<html/>', body)
        headerParts = header.split(utils.CRLF)
        self.assertEquals("HTTP/1.0 200 OK", headerParts[0])
        self.assertTrue(newHeader in headerParts)
        self.assertTrue(utils.ContentTypeHtml in headerParts)

    def testInsertHeaderWithEmptyLines(self):
        def handleRequest(*args, **kwargs):
            yield "HTTP/1.0 200 OK\r\n"
            yield "Header: value\r\n\r\n"
            yield '<ht'
            yield 'ml/>'

        result = list(utils.insertHeader(handleRequest(), 'Set-Cookie: session=dummySessionId1234; path=/'))
        self.assertFalse('' in result, result)

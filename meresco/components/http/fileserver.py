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
from os.path import isfile, join
from rfc822 import formatdate
from time import mktime, gmtime, timezone
from stat import ST_MTIME
from os import stat

from meresco.components.http import utils as httputils

import magic
magicCookie = magic.open(magic.MAGIC_MIME)
magicCookie.load()

import mimetypes
mimetypes.init()

class FileServer:
    def __init__(self, documentRoot):
        self._documentRoot = documentRoot

    def handleRequest(self, port=None, Client=None, RequestURI=None, Method=None, Headers=None, **kwargs):

        if not self.fileExists(RequestURI):
            yield httputils.notFoundHtml
            for line in ['<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">',
"<html><head>",
"<title>404 Not Found</title>",
"</head><body>",
"<h1>Not Found</h1>",
"<p>The requested URL %s was not found on this server.</p>" % RequestURI,
"<hr>",
"<address>Weightless Server at localhost Port 8080</address>",
"</body></html>"]:
                yield line
            raise StopIteration

        filename = self._filenameFor(RequestURI)
        ext = filename.split(".")[-1]
        try:
            contentType = mimetypes.types_map["." + ext]
        except KeyError:
            contentType = "text/plain"

        date = self._date()
        expires = self._date(3600)
        lastModified = formatdate(stat(filename)[ST_MTIME])

        yield ('\r\n'.join([
            'HTTP/1.0 200 OK',
            'Date: %(date)s',
            'Expires: %(expires)s',
            'Last-Modified: %(lastModified)s',
            'Content-Type: %(contentType)s',
            '', ''
        ])) % locals()

        f = open(filename)
        data = f.read(1024)
        while data:
            yield data
            data = f.read(1024)
        f.close()

    def _filenameFor(self, filename):
        while filename and filename[0] == '/':
            filename = filename[1:]
        filename = filename.replace('..', '')
        return join(self._documentRoot, filename)

    def fileExists(self, filename):
        return isfile(self._filenameFor(filename))

    def _date(self, offset=0):
        return formatdate(mktime(gmtime()) - timezone + offset)

class StringServer(object):
    def __init__(self, aString, contentType):
        self._aString = aString
        self._contentType = contentType

    def handleRequest(self, *args, **kwargs):
        yield 'HTTP/1.0 200 OK\r\n'
        yield "Content-Type: %s\r\n" % self._contentType
        yield "\r\n"

        yield self._aString

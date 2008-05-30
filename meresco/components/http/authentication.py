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

from meresco.framework import Observable
from base64 import b64decode

class Authentication(Observable):

    def __init__(self):
        Observable.__init__(self)
        pass

    def handleRequest(self, Headers={}, *args, **kwargs):
        relevantHeader = Headers.get('Authorization', None)
        if relevantHeader == None:
            return REQUEST_AUTHENTICATION_RESPONSE
        else:
            parsed = self._parseHeader(relevantHeader)
            if not parsed:
                return REQUEST_AUTHENTICATION_RESPONSE
            username, password = parsed
            if not self.any.isValidLogin(username, password):
                return REQUEST_AUTHENTICATION_RESPONSE

        return self.all.handleRequest(self, Headers=Headers, *args, **kwargs)

    def _parseHeader(self, header):
        parts = header.split()
        if len(parts) != 2:
            return None
        part0, b64encoded = parts
        if part0 != "Basic":
            return None

        parts = b64decode(b64encoded).split(":", 1)
        if len(parts) != 2:
            return None
        username, password = parts

        return username, password

REQUEST_AUTHENTICATION_RESPONSE = '\r\n'.join([
            "'HTTP/1.0 401 UNAUTHORIZED",
            "Content-Type: text/html; charset=utf-8"
            "", ""]) + """<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>401 Authorization Required</title>
</head><body>
<h1>Authorization Required</h1>
<p>This server could not verify that you
are authorized to access the document
requested.  Either you supplied the wrong
credentials (e.g., bad password), or your
browser doesn't understand how to supply
the credentials required.</p>
</body></html>"""



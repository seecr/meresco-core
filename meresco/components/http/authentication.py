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

    def __init__(self, realm):
        Observable.__init__(self)
        self._realm = realm
        self._validUsers = {}

    def handleRequest(self, Headers={}, *args, **kwargs):
        relevantHeader = Headers.get('Authorization', None)
        if relevantHeader == None:
            yield REQUEST_AUTHENTICATION_RESPONSE % (self._realm, 'Please give username and password.')
            return
        credentials = self._parseHeader(relevantHeader)
        if not credentials in self._validUsers:
            if not self.any.isValidLogin(*credentials):
                yield REQUEST_AUTHENTICATION_RESPONSE % (self._realm, 'Username or password are not valid.')
                return
            else:
                username, password = credentials
                self._validUsers[credentials] = {'name': username}
        yield self.all.handleRequest(Headers=Headers, user=self._validUsers[credentials], *args, **kwargs)

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

REQUEST_AUTHENTICATION_RESPONSE = '\r\n'.join(
    [
        'HTTP/1.0 401 UNAUTHORIZED',
        'Content-Type: text/plain; charset=utf-8',
        'WWW-Authenticate: Basic realm="%s"',
        '',
        '%s'
    ])

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
#
# Query plugin
#
XML_CONTENT_TYPE = 'text/xml; charset="UTF-8"'

class PluginException(Exception):
    def __init__(self, message, contentType = XML_CONTENT_TYPE, errorCode = 500):
        Exception.__init__(self, message)
        self.contentType = contentType
        self.errorCode = errorCode

class QueryPlugin:
    
    def __init__(self, aRequest, aSearchInterface):
        self._request = aRequest
        self.searchInterface = aSearchInterface
        self._arguments = self._request.args
        self.contentType = 'text/plain'
        self.initialize()
        self._request.setResponseCode(200)
        self._request.setHeader('content-type', self.contentType)
        
    def write(self, aString):
        self._request.write(aString)
        
    def getenv(self, key):
        return self._request.getenv(key)
    
    def validate(self):
        pass
    
    def initilize(self):
        raise NotImplementedError()
    
    def process(self):
        pass
        
    def logException(self):
        self._request.logException()
        
    def raiseException(self, message, contentType = 'text/xml; charset="UTF-8"', errorCode = 500):
        raise PluginException(message, contentType, errorCode)
    

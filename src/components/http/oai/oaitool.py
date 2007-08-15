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

from time import gmtime, strftime
from xml.sax.saxutils import escape as xmlEscape
from xml.utils import iso8601

def resumptionTokenFromString(s):
    try:
        result = ResumptionToken()
        result.loadString(s)
        return result
    except ResumptionTokenException, e:
        return None

class ResumptionTokenException(Exception):
    pass

class ResumptionToken:
    
    SHORT = {
        'm': '_metadataPrefix',
        'c': '_continueAt',
        'f': '_from',
        'u': '_until',
        's': '_set'}
    
    def __init__(self,
        _metadataPrefix = '',
        _continueAt = '0',
        _from = '',
        _until = '',
        _set = ''):
        self._metadataPrefix = _metadataPrefix
        self._continueAt = _continueAt
        self._from = _from or '' #blank out "None"
        self._until = _until or ''
        self._set = _set or ''
    
    def __str__(self):
        short = ResumptionToken.SHORT
        return '|'.join(map(lambda k: "%s%s" %(k, self.__dict__[short[k]]), short.keys()))
    
    def __repr__(self):
        return repr(str(self))
    
    def __eq__(self, other):
        return \
            ResumptionToken == other.__class__ and \
            self._metadataPrefix == other._metadataPrefix and \
            self._continueAt == other._continueAt and \
            self._from == other._from and \
            self._until == other._until and \
            self._set == other._set
            
    def loadString(self, s):
        resumptDict = dict(((part[0], part[1:]) for part in s.split('|') if part))
        if set(ResumptionToken.SHORT.keys()) != set(resumptDict.keys()):
            raise ResumptionTokenException()
        for k,v in resumptDict.items():
            setattr(self, ResumptionToken.SHORT[k], v)
                    
class ISO8601Exception(Exception):
    pass

class ISO8601:
    short, long = [len('YYYY-MM-DD'), len('YYYY-MM-DDThh:mm:ssZ')]
    
    def __init__(self, s):
        if not len(s) in [self.short, self.long]:
            raise ISO8601Exception(s)
        try:
            iso8601.parse(s)
        except ValueError, e:
            raise ISO8601Exception(s)
        self.s = s
    
    def _extend(self, extension):
        if not self.isShort():
            return self.s
        return self.s + extension
    
    def floor(self):
        return self._extend("T00:00:00Z")
    
    def ceil(self):
        return self._extend("T23:59:59Z")
    
    def __str__(self):
        return self.floor()
    
    def isShort(self):
        return len(self.s) == self.short


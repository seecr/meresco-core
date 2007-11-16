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
# RSSProfile
from glob import glob
from os.path import join, basename
from urllib import urlencode

DEFAULT_MAXIMUMRECORDS = 15

def readProfilesInDirectory(directoryName):
    profiles = {}
    for f in glob(join(directoryName, '*.rssprofile')):
        name = basename(f)[:-len('.rssprofile')]
        profiles[name] = RSSProfile(f)
    return profiles


class RSSProfile:
    def __init__(self, filename):
        self._read(filename)
        
    def _read(self, filename):
        self._rss = Setters()
        self._rss.sortKeys = None
        self._rss.maximumRecords = DEFAULT_MAXIMUMRECORDS
        self._rss.boxName = ''
        
        self._channel = Setters()
        local = {'rss':self._rss, 'channel': self._channel}
        try:
            execfile(filename, {'__builtins__':{}, 'urlencode': lambda u:urlencode(u, True)}, local)
        except Exception, e:
            raise RSSProfileException(e)
        
        self._item = local.get('item', lambda document: [])
        
    def maximumRecords(self):
        return self._rss.maximumRecords
    
    def sortKeys(self):
        return self._rss.sortKeys
    
    def boxName(self):
        return self._rss.boxName
    
    def item(self, document):
        return self._item(document)
    
    def channel(self):
        return self._channel
    
class RSSProfileException(Exception):
    pass

class Setters(object):
    def __init__(self):
        object.__init__(self)
        self._attributes = []
    
    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)
        if key[0] != '_': 
            self._attributes.append((key, value))
    
    def listAttributes(self):
        return self._attributes
    
    def __getitem__(self, key, default = None):
        return getattr(self, key, default)
            

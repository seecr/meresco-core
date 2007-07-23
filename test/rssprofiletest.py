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

import unittest
from meresco.legacy.plugins.rssprofile import RSSProfile, RSSProfileException, readProfilesInDirectory
from cStringIO import StringIO
from tempfile import mkdtemp
from shutil import rmtree
from os.path import join
from cq2utils.wrappers import wrapp
from amara.binderytools import bind_string


TESTRSSProfile = """#
# General settings for RSS 
#
rss.sortKeys = 'generic4,,1'
rss.maximumRecords = 15

#
# Channel (header of RSS)
#
channel.description = 'The Description'
channel.link = 'http://example.org/rss'
channel.title = 'The RSS Title'

#
# Item
#
def item(document):
    return [ 
        ('title', document.xmlfields.dctitle),
        ('url', 'http://example.org?' + urlencode({'id':document.xmlfields.general.identifier}))
    ]
"""

XMLDOCUMENT = wrapp(bind_string("""<document>
<xmlfields>
  <dctitle>The title</dctitle>
    <general><identifier>&lt;ID&gt;</identifier></general>
</xmlfields>
</document>""")).document

class RSSProfileTest(unittest.TestCase):
    
    def setUp(self):
        self._directoryname = mkdtemp()
        
    def tearDown(self):
        rmtree(self._directoryname)
    
    def testReadProfile(self):
        self._writeFile('test.rssprofile', TESTRSSProfile)
        profile = RSSProfile(join(self._directoryname, 'test.rssprofile'))
        self.assertEquals('generic4,,1', profile.sortKeys())
        self.assertEquals(15, profile.maximumRecords())
        self.assertEquals({'title':'The RSS Title', 'description':'The Description', 'link':'http://example.org/rss'}, dict(profile.channel().listAttributes()))
        
        result = profile.item(XMLDOCUMENT)
        self.assertEquals({'url':'http://example.org?id=%3CID%3E', 'title':'The title'}, dict(result))
        
    def testProfileEmpty(self):
        self._writeFile("empty", "")
        profile = RSSProfile(join(self._directoryname, "empty"))
        self.assertEquals(None, profile.sortKeys())
        self.assertEquals(15, profile.maximumRecords())
        self.assertEquals([], profile.channel().listAttributes())
        self.assertEquals([], profile.item(XMLDOCUMENT))
            
    def testProfileErrors(self):
        for errorline in ["channel = Bla", "item"]:
            self._writeFile("broken", errorline)
            try:
                profile = RSSProfile(join(self._directoryname, "broken"))
                self.fail()
            except RSSProfileException:
                pass
            
    def testReadProfilesInDirectory(self):
        self._writeFile('default.rssprofile', "channel.title='Default'")
        self._writeFile('test1.rssprofile', "channel.title='Test1'")
        profiles = readProfilesInDirectory(self._directoryname)
        self.assertEquals(set(['default','test1']), set(profiles.keys()))
        self.assertEquals('Default', profiles['default'].channel()['title'])
        self.assertEquals('Test1', profiles['test1'].channel()['title'])
        
    def testReadEmptyDirectory(self):
        profiles = readProfilesInDirectory(self._directoryname)
        self.assertEquals({}, profiles)
        
    def _writeFile(self, filename, contents):
        f=open(join(self._directoryname, filename), 'w')
        try:
            f.write(contents)
        finally:
            f.close()

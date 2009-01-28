#!/usr/bin/env python2.5
## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2009 Seek You Too (CQ2) http://www.cq2.nl
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
from cq2utils import CQ2TestCase, CallTrace
from merescocore.components import StorageComponent, Reindex, FilterMessages
from merescocore.framework import be

from os.path import join
from os import makedirs

class ReindexTest(CQ2TestCase):
    def testEnumerateStorage(self):
        storage = StorageComponent(self.tempdir)
        storage.add('identifier:A', 'part', 'data1')
        storage.add('identifier:B', 'part', 'data2')
        storage.add('identifier:C', 'part', 'data3')
        self.assertEquals(set(['identifier:B', 'identifier:C', 'identifier:A']), set(storage.listIdentifiers()))
        observer = CallTrace('observer')
        reindex = be(
            (Reindex('part'),
                (FilterMessages(allowed=['listIdentifiers']),
                    (storage, ),
                ),
                (observer,)
            )
        )
        result = list(reindex.reindex())
        self.assertEquals(3, len(observer.calledMethods))
        methods = sorted(map(str, observer.calledMethods))
        self.assertEquals("add('identifier:A', 'ignoredName', <etree._ElementTree>)", methods[0])
        self.assertEquals("add('identifier:B', 'ignoredName', <etree._ElementTree>)", methods[1])
        self.assertEquals("add('identifier:C', 'ignoredName', <etree._ElementTree>)", methods[2])

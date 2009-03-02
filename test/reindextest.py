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

class ReindexTest(CQ2TestCase):

    def setupStorage(self, records):
        storage = StorageComponent(self.tempdir)
        for record in records:
            storage.add(*record)
        return storage

    def setupDna(self, storage):
        observer = CallTrace('observer')
        reindex = be(
            (Reindex('part'),
                (FilterMessages(allowed=['listIdentifiers']),
                    (storage, ),
                ),
                (observer,)
            )
        )
        return reindex, observer

    def testEnumerateStorage(self):
        storage = self.setupStorage([
            ('identifier:A', 'part', 'data1'),
            ('identifier:B', 'part', 'data2'),
            ('identifier:C', 'part', 'data3'),
        ])
        self.assertEquals(set(['identifier:B', 'identifier:C', 'identifier:A']), set(storage.listIdentifiers()))

        reindex, observer = self.setupDna(storage)
        result = list(reindex.reindex())
        self.assertEquals(3, len(observer.calledMethods))
        methods = sorted(map(str, observer.calledMethods))
        self.assertEquals("add('identifier:A', 'ignoredName', <etree._ElementTree>)", methods[0])
        self.assertEquals("add('identifier:B', 'ignoredName', <etree._ElementTree>)", methods[1])
        self.assertEquals("add('identifier:C', 'ignoredName', <etree._ElementTree>)", methods[2])

    def testSelectIdentifiers(self):
        storage = self.setupStorage([
            ('identifier:1A', 'part', 'data1'),
            ('identifier:1B', 'part', 'data2'),
            ('identifier:2C', 'part', 'data3'),
        ])
        reindex, observer = self.setupDna(storage)
        result = list(reindex.reindex(partialIdentifier="identifier:1"))
        self.assertEquals(2, len(observer.calledMethods))

        observer.calledMethods = []
        result = list(reindex.reindex(partialIdentifier="identifier:2"))
        self.assertEquals(1, len(observer.calledMethods))

        observer.calledMethods = []
        result = list(reindex.reindex(partialIdentifier="identifier:"))
        self.assertEquals(3, len(observer.calledMethods))

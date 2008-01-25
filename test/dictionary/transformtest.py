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
from meresco.components.dictionary.transform import CleanSplit, years
from meresco.components.dictionary import Transform, DocumentField

from cq2utils import CallTrace

import unittest

class TransformTest(unittest.TestCase):

    def testNoSourceMatches(self):
        observer = CallTrace("observer")
        transform = Transform([('source', 'target', lambda x: ['transformed %s'  % x])])
        transform.addObserver(observer)
        transform.addField("id", DocumentField('not the source', 'value'))
        self.assertEquals(1, len(observer.calledMethods))

        self.assertEquals(DocumentField('not the source', 'value'), observer.calledMethods[0].arguments[1])

    def testMultipleRules(self):
        observer = CallTrace("observer")
        transform = Transform([
            ('source', 'target', lambda x: ['transformed %s'  % x]),
            ('source', 'target2', lambda x: ['transformed2 %s'  % x]),
        ])
        transform.addObserver(observer)
        transform.addField("id", DocumentField('source', 'value'))
        self.assertEquals(3, len(observer.calledMethods))

        self.assertEquals(DocumentField('source', 'value'), observer.calledMethods[0].arguments[1])
        self.assertEquals(DocumentField('target', 'transformed value'), observer.calledMethods[1].arguments[1])
        self.assertEquals(DocumentField('target2', 'transformed2 value'), observer.calledMethods[2].arguments[1])

    def testNoTransformation(self):
        observer = CallTrace("observer")
        transform = Transform([('source', 'target', lambda x: [])])
        transform.addObserver(observer)
        transform.addField("id", DocumentField('source', 'value'))
        self.assertEquals(1, len(observer.calledMethods))

        self.assertEquals(DocumentField('source', 'value'), observer.calledMethods[0].arguments[1])

    def testMultipleTransformations(self):
        observer = CallTrace("observer")
        transform = Transform([
            ('source', 'target', lambda x: ['transformed %s'  % x, 'transformed2 %s'  % x]),
        ])
        transform.addObserver(observer)
        transform.addField("id", DocumentField('source', 'value'))
        self.assertEquals(3, len(observer.calledMethods))

        self.assertEquals(DocumentField('source', 'value'), observer.calledMethods[0].arguments[1])
        self.assertEquals(DocumentField('target', 'transformed value'), observer.calledMethods[1].arguments[1])
        self.assertEquals(DocumentField('target', 'transformed2 value'), observer.calledMethods[2].arguments[1])

    def testOptionsArePreserved(self):
        observer = CallTrace("observer")
        transform = Transform([
            ('source', 'target', lambda x: ['transformed %s'  % x]),
        ])
        transform.addObserver(observer)
        transform.addField("id", DocumentField('source', 'value', option="an option"))
        self.assertEquals(2, len(observer.calledMethods))

        self.assertEquals(DocumentField('source', 'value', option="an option"), observer.calledMethods[0].arguments[1])
        self.assertEquals(DocumentField('target', 'transformed value', option="an option"), observer.calledMethods[1].arguments[1])

    def testCleanSplit(self):
        self.assertEquals(['some', 'thing'], list(CleanSplit(';')('some;thing')))

    def testYears(self):
        self.assertEquals([], years('garbage'))
        self.assertEquals(['2000'], years('2000'))
        self.assertEquals(['2000', '2001'], years('2000-2001'))
        self.assertEquals(['2000'], years('2000-01-01'))
        self.assertEquals(['2000'], years('2000-01-01T23:32:12Z'))

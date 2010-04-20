# -*- coding: utf-8 -*-
## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
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

from __future__ import with_statement

from meresco.core import Observable
from lxml.etree import parse
from StringIO import StringIO
from os.path import isdir, join
from os import makedirs, listdir, remove, rmdir

EMPTYDOC = parse(StringIO('<empty/>'))

class Reindex(Observable):

    def __init__(self, partName, filelistPath=''):
        Observable.__init__(self)
        self._partName = partName
        self._filelistPath = filelistPath
        if not isdir(self._filelistPath):
            makedirs(self._filelistPath)

    def handleRequest(self, *args, **kwargs):
        arguments = kwargs.get('arguments', {})
        try:
            session = arguments.get('session', [''])[0]
        except IndexError:
            session = ''

        batchSize = int(arguments.get('batchsize', [200])[0])
        yield "HTTP/1.0 200 OK\r\nContent-Type: plain/text\r\n\r\n"
        if session == '':
            yield "!error: session missing"
            return
        if batchSize > 2000  or batchSize <= 0:
            yield "!error: invalid batchsize"
            return

        sessionDirectory = join(self._filelistPath, session)
        if not isdir(sessionDirectory):
            results = self._createBatches(sessionDirectory, batchSize)
        else:
            results = self._processBatches(sessionDirectory)

        for result in results:
            yield result


    def _createBatches(self, sessionDirectory, batchSize):
        currentBatch = 0
        batch = []
        identifiersFound = False

        for identifier in self.any.listIdentifiers(self._partName):
            batch.append(identifier)
            if len(batch) == batchSize:
                identifiersFound = self._writeBatch(sessionDirectory, currentBatch, batch)
                yield "#"
                currentBatch += 1
                batch = []
        additionalBatch = 0
        if batch != []:
            identifiersFound = self._writeBatch(sessionDirectory, currentBatch, batch)
            additionalBatch = 1
            yield "#"
        if not identifiersFound:
            yield "!error: no identifiers"
            return
        yield '\n=batches: %d' % (currentBatch + additionalBatch)

    def _writeBatch(self, sessionDirectory, number, batch):
        if not isdir(sessionDirectory):
            makedirs(sessionDirectory)

        with open(join(sessionDirectory, 'batch_%0.15d' % number), 'w') as fd:
            fd.write('\n'.join(batch))
        return True

    def _processBatches(self, sessionDirectory):
        batchFile = join(sessionDirectory, listdir(sessionDirectory)[0])

        for identifier in (identifier.strip() for identifier in open(batchFile).readlines()):
            try:
                self.do.addDocumentPart(identifier=identifier, name='ignoredName', lxmlNode=EMPTYDOC)
            except Exception, e:
                yield '\n!error processing "%s": %s' % (identifier, str(e))
                return
            yield "+%s\n" % identifier

        remove(batchFile)
        yield "=batches left: %d" % len(listdir(sessionDirectory))
        if len(listdir(sessionDirectory)) == 0:
            rmdir(sessionDirectory)

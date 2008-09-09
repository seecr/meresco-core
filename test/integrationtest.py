#!/usr/bin/env python
# encoding: utf-8
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
import os, sys
os.system('find .. -name "*.pyc" | xargs rm -f')

from glob import glob
for path in glob('../deps.d/*'):
    sys.path.insert(0, path)

sys.path.insert(0, "..")

from os import system
from sys import exit, exc_info

from os.path import isdir, isfile

from unittest import main
from random import randint
from time import time
from glob import glob

from amara.binderytools import bind_file, bind_string

from weightless import Reactor
from cq2utils import CQ2TestCase, getRequest, postRequest, wheelOfTime

from meresco.framework import be

from meresco.examples.dna.server import dna, config

integrationTempdir = '/tmp/meresco-integration-test'
reactor = Reactor()

class IntegrationTest(CQ2TestCase):

    def testExplain(self):
        header, body = getRequest(reactor, port, '/sru', {})
        explainResponse = body.explainResponse
        self.assertEquals(config['host'], str(explainResponse.record.recordData.explain.serverInfo.host))

        portNumber = int(explainResponse.record.recordData.explain.serverInfo.port)
        self.assertTrue(50000 < portNumber < 60000, portNumber)

    def testIndex(self):
        self.assertSruQuery(2, 'dc="Seek You Too"')
        self.assertSruQuery(2, 'dc.title = program')
        self.assertSruQuery(1, 'dc.identifier="http://meresco.com?record=2"')

    def testDrilldown(self):
        result = self.doDrilldown('dc.rights="Open Source"', 'dc.subject')
        navigator = result.extraResponseData.drilldown.term_drilldown.navigator

        self.assertEquals(1, len(navigator), result.xml())
        self.assertEquals('dc.subject', str(navigator.name))
        self.assertEquals(2, len(navigator.item))
        itemValues = [(item.count, str(item)) for item in navigator.item]
        self.assertEquals([(1, 'Programming'), (1, 'Search')], itemValues)

    def testRSS(self):
        body = self._doQuery({'query': 'dc.title = program'}, path="/rss")
        items = [(str(item.title), str(item.description), str(item.link).split('?', 1)[1]) for item in body.rss.channel.item]
        self.assertEquals(2, len(items))
        self.assertEquals([('Example Program 1', 'This is an example program about Search with Meresco', 'operation=searchRetrieve&version=1.1&query=dc.identifier%3Dhttp%3A//meresco.com%3Frecord%3D1'), ('Example Program 2', 'This is an example program about Programming with Meresco', 'operation=searchRetrieve&version=1.1&query=dc.identifier%3Dhttp%3A//meresco.com%3Frecord%3D2')], items)

    def doDrilldown(self, query, drilldownField):
        message = self._doQuery({'query':query, 'x-term-drilldown': drilldownField})
        result = message.searchRetrieveResponse
        return result

    def assertSruQuery(self, numberOfRecords, query):
        message = self._doQuery({'query':query})
        result = message.searchRetrieveResponse
        self.assertEquals(numberOfRecords, int(str(result.numberOfRecords)))
        return result

    def _doQuery(self, arguments, path="/sru"):
        queryArguments = {'version': '1.1', 'operation': 'searchRetrieve'}
        queryArguments.update(arguments)
        header, body = getRequest(reactor, port, path, queryArguments)
        return body

def createDatabase(port):
    recordPacking = 'xml'
    start = time()
    print "Creating database in", integrationTempdir
    sourceFiles = glob('sahara_output/*.updateRequest')
    for updateRequestFile in sorted(sourceFiles):
        print 'Sending:', updateRequestFile
        header, body = postRequest(reactor, port, '/update', open(updateRequestFile).read())
        if '200 Ok' not in header:
            print 'No 200 Ok response, but:'
            print header
            exit(123)
        if "srw:diagnostics" in body.xml():
            print body.xml()
            exit(1234)
    print "Finished creating database in %s seconds" % (time() - start)
    print "Giving the server index some time for a auto refresh"
    wheelOfTime(reactor, 2)

    print "Finished creating database"

if __name__ == '__main__':
    from sys import argv
    if not '--fast' in argv:
        system('rm -rf ' + integrationTempdir)
        system('mkdir --parents '+ integrationTempdir)

    port = randint(50000,60000)
    server = be(dna(reactor, config['host'], portNumber=port, databasePath=integrationTempdir))
    server.once.observer_init()

    if '--fast' in argv and isdir(integrationTempdir):
        argv.remove('--fast')
        print "Reusing database in", integrationTempdir
    else:
        createDatabase(port)
    main()

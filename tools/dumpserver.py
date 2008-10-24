#!/usr/bin/env python2.5
from __future__ import with_statement

from glob import glob
from sys import path, argv, exit
for directory in glob('../deps.d/*'):
    path.insert(0, directory)
path.insert(0, '..')

from weightless import Reactor
from sys import stdout
from os.path import abspath, dirname, join, isdir, basename
from os import makedirs
from meresco.components.http import ObservableHttpServer
from meresco.components.http.webrequestserver import WebRequestServer
from meresco.components.sru import SRURecordUpdate
from meresco.framework import Observable, be
from re import compile
from traceback import format_exc
from amara.binderytools import bind_stream

mydir = dirname(abspath(__file__))
notWordCharRE = compile('\W+')

class Dump(SRURecordUpdate):
    def __init__(self, dumpdir):
        SRURecordUpdate.__init__(self)
        self._dumpdir = dumpdir
        self._number = self._findLastNumber()

    def handleRequest(self, httpRequest):
        try:
            updateRequest = bind_stream(httpRequest.content).updateRequest
            recordId = str(updateRequest.recordIdentifier)
            normalizedRecordId = notWordCharRE.sub('_', recordId)
            self._number +=1
            filename = '%05d_%s.updateRequest' %(self._number, normalizedRecordId)
            with open(join(self._dumpdir, filename), 'w') as f:
                print recordId
                stdout.flush()
                updateRequest.xml(f)
            self.writeSucces(httpRequest)
        except Exception, e:
            self.writeError(httpRequest, format_exc(limit=7))

    def _findLastNumber(self):
        return max([int(basename(f)[:5]) for f in glob(join(self._dumpdir, '*.updateRequest'))]+[0])


def main(reactor, portNumber, dumpdir):
    isdir(dumpdir) or makedirs(dumpdir)
    server = be(
        (Observable(),
            (ObservableHttpServer(reactor, portNumber),
                (WebRequestServer(),
                    (Dump(dumpdir),)
                )
            )
        )
    )
    server.once.observer_init()

if __name__== '__main__':
    args = argv[1:]
    if len(args) != 2:
        print "Usage %s <portnumber> <dumpdir>" % argv[0]
        exit(1)
    portNumber = int(args[0])
    dumpdir = args[1]
    reactor = Reactor()
    main(reactor, portNumber, dumpdir)
    print 'Ready to rumble the dumpserver at', portNumber
    print '  - dumps are written to', dumpdir
    stdout.flush()
    reactor.loop()

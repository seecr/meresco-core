# -*- coding: utf-8 -*-
## begin license ##
#
# "Meresco Core" is an open-source library containing components to build searchengines, repositories and archives.
#
# Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007 SURFnet. http://www.surfnet.nl
# Copyright (C) 2007-2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2011-2012, 2020 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2011 Stichting Kennisnet http://www.kennisnet.nl
#
# This file is part of "Meresco Core"
#
# "Meresco Core" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco Core" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco Core"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from meresco.core import Observable

from weightless.core import DeclineMessage, methodOrMethodPartialStr

class ResourceManager(Observable):

    def __init__(self, transactionName, name=None):
        Observable.__init__(self, name=name)
        self._transactionName = transactionName
        self.txs = {}

    def begin(self, name):
        if name != self._transactionName:
            return
        tx = self.ctx.tx
        resourceTx = yield self.any.beginTransaction()
        self.txs[tx.getId()] = resourceTx
        tx.join(self)

    def all_unknown(self, message, *args, **kwargs):
        tx = self.ctx.tx
        method = getattr(self.txs[tx.getId()], message, None)
        if method != None:
            _ = yield method(*args, **kwargs)
            # assert required as Transaction is no Observable
            assert _ is None, "%s returned '%s'" % (methodOrMethodPartialStr(method), _)

    def any_unknown(self, message, *args, **kwargs):
        tx = self.ctx.tx
        method = getattr(self.txs[tx.getId()], message, None)
        if method != None:
            response = yield method(*args, **kwargs)
            return response
        raise DeclineMessage

    def do_unknown(self, message, *args, **kwargs):
        tx = self.ctx.tx
        method = getattr(self.txs[tx.getId()], message, None)
        if method != None:
            method(*args, **kwargs)

    def call_unknown(self, message, *args, **kwargs):
        tx = self.ctx.tx
        method = getattr(self.txs[tx.getId()], message, None)
        if method != None:
            return method(*args, **kwargs)
        raise DeclineMessage

    def commit(self, id):
        resourceTx = self.txs.pop(id)
        return resourceTx.commit()

    def rollback(self, id):
        resourceTx = self.txs.pop(id)
        return resourceTx.rollback()


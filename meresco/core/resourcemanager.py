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
from observable import Observable
from callstackscope import callstackscope

class ResourceManager(Observable):

    def __init__(self, transactionName, resourceTxFactory):
        Observable.__init__(self)
        self._resourceTxFactory = resourceTxFactory
        self._transactionName = transactionName
        self.txs = {}

    def begin(self):
        tx = self.ctx.tx
        if tx.name != self._transactionName:
            return
        resourceTx = self._resourceTxFactory(self)
        tx.join(self)
        self.txs[tx.getId()] = resourceTx

    def unknown(self, message, *args, **kwargs):
        tx = self.ctx.tx
        method = getattr(self.txs[tx.getId()], message, None)
        if method != None:
            yield method(*args, **kwargs)

    def commit(self):
        tx = self.ctx.tx
        resourceTx = self.txs.pop(tx.getId())
        resourceTx.commit()

    def rollback(self):
        tx = self.ctx.tx
        resourceTx = self.txs.pop(tx.getId())
        resourceTx.rollback()


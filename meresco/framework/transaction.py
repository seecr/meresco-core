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
from meresco.framework import Observable

class TransactionException(Exception):
    pass

class ResourceManager(Observable):

    def __init__(self, resourceTxFactory):
        Observable.__init__(self)
        self._resourceTxFactory = resourceTxFactory
        self.txs = {}

    def begin(self, tx):
        resourceTx = self._resourceTxFactory(self)
        tx.join(resourceTx)
        self.txs[self.tx.getId()] = resourceTx

    def unknown(self, message, *args, **kwargs):
        try:
            method = getattr(self.txs[self.tx.getId()], message)
            yield method(*args, **kwargs)
        except AttributeError:
            pass

class Transaction(object):

    def __init__(self):
        self.resourceTxs = []
        self.locals = {}

    def getId(self):
        return id(self)

    def join(self, resourceTx):
        if resourceTx not in self.resourceTxs:
            self.resourceTxs.append(resourceTx)

    def commit(self):
        for resourceTx in self.resourceTxs:
            resourceTx.commit()

    def rollback(self):
        for resourceTx in self.resourceTxs:
            resourceTx.rollback()

class TransactionScope(Observable):

    def unknown(self, name, *args, **kwargs):
        __callstack_var_tx__ = Transaction()
        self.once.begin(__callstack_var_tx__)
        try:
            for result in self.all.unknown(name, *args, **kwargs):
                yield result
            __callstack_var_tx__.commit()
        except TransactionException, te:
            __callstack_var_tx__.rollback()



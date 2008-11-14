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

    def __init__(self, transactionName, resourceTxFactory):
        Observable.__init__(self)
        self._resourceTxFactory = resourceTxFactory
        self._transactionName = transactionName
        self.txs = {}

    def begin(self):
        if self.tx.name != self._transactionName:
            return
        resourceTx = self._resourceTxFactory(self)
        self.tx.join(self)
        self.txs[self.tx.getId()] = resourceTx

    def unknown(self, message, *args, **kwargs):
        method = getattr(self.txs[self.tx.getId()], message, None)
        if method != None:
            yield method(*args, **kwargs)

    def commit(self):
        resourceTx = self.txs.pop(self.tx.getId())
        resourceTx.commit()
        
    def rollback(self):
        resourceTx = self.txs.pop(self.tx.getId())
        resourceTx.rollback()

class Transaction(object):

    def __init__(self, name):
        self._resourceManagers = []
        self.locals = {}
        self.name = name

    def getId(self):
        return id(self)

    def join(self, resourceManager):
        if resourceManager not in self._resourceManagers:
            self._resourceManagers.append(resourceManager)

    def commit(self):
        while self._resourceManagers:
            resourceManager = self._resourceManagers.pop(0)
            resourceManager.commit()

    def rollback(self):
        while self._resourceManagers:
            resourceManager = self._resourceManagers.pop(0)
            resourceManager.rollback()

    def abort(self):
        raise TransactionException()

class TransactionScope(Observable):
    def __init__(self, transactionName):
        Observable.__init__(self)
        self._transactionName = transactionName

    def unknown(self, message, *args, **kwargs):
        __callstack_var_tx__ = Transaction(self._transactionName)
        self.once.begin()
        try:
            for result in self.all.unknown(message, *args, **kwargs):
                yield result
            __callstack_var_tx__.commit()
        except TransactionException:
            __callstack_var_tx__.rollback()


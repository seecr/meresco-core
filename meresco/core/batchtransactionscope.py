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
from transaction import TransactionException, Transaction
from warnings import warn

class BatchTransactionScope(Observable):
    def __init__(self, transactionName, reactor, batchSize=10, timeout=1):
        warn("BatchTransactionScope is not fit for suspendable commits in timeOuts.", DeprecationWarning)
        Observable.__init__(self)
        assert timeout > 0
        self._transactionName = transactionName
        self._reactor = reactor
        self._batchSize = batchSize
        self._timeout = timeout
        self._currentTransaction = None

    def unknown(self, message, *args, **kwargs):
        __callstack_var_tx__ = transaction = self._currentTransaction
        if transaction == None:
            self._currentTransaction = __callstack_var_tx__ = transaction = Transaction(self._transactionName)
            transaction._batchCounter = 0
            transaction._activeGenerators = 0
            transaction._markedForCommit = False
            transaction._timerToken = None
            self.once.begin()
        try:
            transaction._activeGenerators += 1
            results = self.all.unknown(message, *args, **kwargs)
            for result in results:
                yield result
            transaction._activeGenerators -= 1

            transaction._batchCounter += 1
            if transaction._markedForCommit or transaction._batchCounter >= self._batchSize:
                yield self._commit(transaction)
            else:
                self._removeTimer(transaction)
                transaction._timerToken = self._reactor.addTimer(self._timeout,
                                                                 lambda: self._doTimeout(transaction))
        except TransactionException:
            transaction.rollback()
            self._currentTransaction = None
        finally:
            results = None

    def _doTimeout(self, transaction):
         transaction._timerToken = None
         list(self._commit(transaction))

    def _commit(self, transaction):
        transaction._markedForCommit = True
        self._removeTimer(transaction)
        if transaction == self._currentTransaction:
            self._currentTransaction = None
        if transaction._activeGenerators == 0:
            for result in transaction.commit():
                yield result

    def _removeTimer(self, transaction):
        if transaction._timerToken != None:
            self._reactor.removeTimer(transaction._timerToken)

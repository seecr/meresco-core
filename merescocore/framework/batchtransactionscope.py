# -*- coding: utf-8 -*-
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
from merescocore.framework import Observable
from transaction import TransactionException, Transaction

class BatchTransactionScope(Observable):
    def __init__(self, transactionName, reactor, batchSize=10, timeout=1):
        Observable.__init__(self)
        assert timeout > 0
        self._transactionName = transactionName
        

    def unknown(self, message, *args, **kwargs):
        __callstack_var_tx__ = Transaction(self._transactionName)
        self.once.begin()
        try:
            results = self.all.unknown(message, *args, **kwargs)
            for result in results:
                yield result
            __callstack_var_tx__.commit()
        except TransactionException:
            __callstack_var_tx__.rollback()
        finally:
            results = None


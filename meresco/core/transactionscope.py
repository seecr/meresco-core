# -*- coding: utf-8 -*-
## begin license ##
#
# "Meresco Core" is an open-source library containing components to build searchengines, repositories and archives.
#
# Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007 SURFnet. http://www.surfnet.nl
# Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2010, 2020-2021 Stichting Kennisnet https://www.kennisnet.nl
# Copyright (C) 2011-2012, 2020-2021 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2020-2021 Data Archiving and Network Services https://dans.knaw.nl
# Copyright (C) 2020-2021 SURF https://www.surf.nl
# Copyright (C) 2020-2021 The Netherlands Institute for Sound and Vision https://beeldengeluid.nl
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

from weightless.core import NoneOfTheObserversRespond, DeclineMessage
from meresco.core import Observable
from .transaction import TransactionException, Transaction


class TransactionScope(Observable):

    def __init__(self, transactionName, name=None):
        Observable.__init__(self, name=transactionName if name is None else name)
        self._transactionName = transactionName

    def all_unknown(self, message, *args, **kwargs):
        __callstack_var_tx__ = Transaction(name=self._transactionName)
        yield self.once.begin(self._transactionName)
        try:
            yield self.all.unknown(message, *args, **kwargs)
            yield __callstack_var_tx__.commit()
        except TransactionException:
            yield __callstack_var_tx__.rollback()

    def any_unknown(self, message, *args, **kwargs):
        __callstack_var_tx__ = Transaction(name=self._transactionName)
        yield self.once.begin(name=self._transactionName)
        try:
            try:
                response = yield self.any.unknown(message, *args, **kwargs)
            except NoneOfTheObserversRespond:
                raise DeclineMessage
            yield __callstack_var_tx__.commit()
            return response
        except TransactionException:
            yield __callstack_var_tx__.rollback()


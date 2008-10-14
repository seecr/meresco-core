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

class TransactionFactory(Observable):

    def __init__(self, factoryMethod):
        Observable.__init__(self)
        self._factoryMethod = factoryMethod
        self.txs = {}

    def begin(self):
        self.txs[self.tx.getId()] = self._factoryMethod(self)

    def unknown(self, message, *args, **kwargs):
        try:
            method = getattr(self.txs[self.tx.getId()], message)
            yield method(*args, **kwargs)
        except AttributeError:
            pass

    def commit(self):
        self.txs[self.tx.getId()].finalize()
        del self.txs[self.tx.getId()]

    def rollback(self):
        self.txs[self.tx.getId()].rollback()
        del self.txs[self.tx.getId()]

class __Transaction__(object):

    def getId(self):
        return id(self)

class TransactionScope(Observable):

    def unknown(self, name, *args, **kwargs):
        __callstack_var_tx__ = __Transaction__()
        self.once.begin()
        try:
            for result in self.all.unknown(name, *args, **kwargs):
                yield result
            self.once.commit()
        except TransactionException, te:
            self.once.rollback()



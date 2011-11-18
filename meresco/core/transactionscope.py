# -*- coding: utf-8 -*-
## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2010 Stichting Kennisnet http://www.kennisnet.nl
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

class TransactionScope(Observable):
   
    @identify
    def driver(self, gen):
        this = yield
        g = compose(gen)
        for _ in g:
            assert _ in (None, Yield, Callable)
            if callable(_):
                _(reactor, this.next)
            yield

    def timerfired(self, reactor):
        def process(self):
            yield __callstack_var_tx__.commit()
            yield Reactor.removeProcess
        reactor.addProcess(self.driver(self.process()).next)

    def all_unknown(self, reactor, message, *args, **kwargs):
        __callstack_var_tx__ = Transaction(self.observable_name())
        yield self.once.begin()
        try:
            yield self.all.unknown(message, *args, **kwargs)
            yield __callstack_var_tx__.commit()
        except TransactionException:
            yield __callstack_var_tx__.rollback()

# -*- coding: utf-8 -*-
## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2011 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2010-2011 Stichting Kennisnet http://www.kennisnet.nl
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

from meresco.core import Observable, TransactionScope, Transparent
from meresco.core.observable import be
from unittest import TestCase

class ObservableTest(TestCase):

    def testOneTransactionPerGenerator(self):
        txId = []
        class MyTxParticipant(Observable):
            def doSomething(self):
                txId.append(self.ctx.tx.getId())
                yield 'A'
                txId.append(self.ctx.tx.getId())
                yield 'B'
        dna = \
            (Observable(),
                (TransactionScope('name'),
                    (MyTxParticipant(),)
                )
            )
        body = be(dna)
        scope1 = body.all.doSomething()
        scope2 = body.all.doSomething()
        scope1.next()
        scope2.next()
        scope1.next()
        scope2.next()
        self.assertTrue(txId[0] != txId[1])
        self.assertTrue(txId[1] > 0)
        self.assertTrue(txId[0] > 0)
        self.assertEquals(txId[0], txId[2])
        self.assertEquals(txId[1], txId[3])

    def testTransactionCommit(self):
        collected = {}
        class MyFirstTxParticipant(Transparent):
            def begin(self):
                self.ctx.tx.join(self)
            def doSomething(self):
                collected[self.ctx.tx.getId()] = ['first']
                yield self.any.doSomething()
            def commit(self):
                collected[self.ctx.tx.getId()].append('done 1')
        class MySecondTxParticipant(Observable):
            def begin(self):
                self.ctx.tx.join(self)
            def doSomething(self):
                collected[self.ctx.tx.getId()].append('second')
                yield 'second'
            def commit(self):
                collected[self.ctx.tx.getId()].append('done 2')
        dna = \
            (Observable(),
                (TransactionScope('name'),
                    (MyFirstTxParticipant(),
                        (MySecondTxParticipant(),)
                    )
                )
            )
        body = be(dna)
        list(body.all.doSomething())
        self.assertEquals(['first', 'second', 'done 1', 'done 2'], collected.values()[0])

    def testResolveCallStackVariables(self):
        class StackVarHolder(Observable):
            def unknown(self, name, *args, **kwargs):
                __callstack_var_myvar__ = []
                for result in self.all.unknown(name, *args, **kwargs):
                    pass
                yield __callstack_var_myvar__

        class StackVarUser(Observable):
            def useVariable(self):
                self.ctx.myvar.append('Thingy')

        dna = \
            (Observable(),
                (StackVarHolder(),
                    (StackVarUser(),)
                )
            )
        root = be(dna)
        self.assertEquals(['Thingy'], root.any.useVariable())

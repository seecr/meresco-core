## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2011 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2011 Stichting Kennisnet http://www.kennisnet.nl
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

from cq2utils import CallTrace
from unittest import TestCase
from meresco.core import ResourceManager, be, Observable, TransactionScope, TransactionException, Transaction

from weightless.core import compose

class TransactionTest(TestCase):
    def testOne(self):
        traces = []
        class AResource(object):
            class MyTransaction(object):
                def g(self):
                    traces.append('g')
                def commit(self):
                    traces.append('commit')
            def beginTransaction(self):
                traces.append('begin')
                raise StopIteration(AResource.MyTransaction())
                yield
        class InBetween(Observable):
            def f(self):
                yield self.all.g()
                yield self.all.g()
        dna = \
            (Observable(),
                (TransactionScope("transactionName"),
                    (InBetween(),
                        (ResourceManager("transactionName"),
                            (AResource(),)
                        )
                    )
                )
            )
        body = be(dna)
        result = list(compose(body.all.f()))
        self.assertEquals(4, len(traces))
        self.assertEquals(['begin', 'g', 'g', 'commit'], traces)

    def testResourceManagerHandlesAttributeError(self):
        class Resource(object):
            def beginTransaction(self):
                raise StopIteration(object())
                yield
        rm = ResourceManager('transaction')
        rm.addObserver(Resource())
        __callstack_var_tx__ = CallTrace('TransactionScope')
        list(compose(rm.begin('transaction')))
        try:
            list(compose(rm.all.unknown('doesnotexist')))
        except AttributeError:
            self.fail('ResourceManager must ignore unknown methods.')

    def testJoinOnlyOnce(self):
        commitCalled = []
        class MockResourceManager(object):
            def commit(self, id):
                commitCalled.append(id)
        tx = Transaction('name')
        resource = MockResourceManager()
        tx.join(resource)
        tx.join(resource)
        list(tx.commit())
        self.assertEquals(1, len(commitCalled))
        self.assertEquals(tx.getId(), commitCalled[0])

    def testFreeTransaction(self):
        resourceManager = ResourceManager('name')
        resourceTx = CallTrace('resourceTx')
        class Resource(object):
            def beginTransaction(self):
                raise StopIteration(resourceTx)
                yield
        dna = \
            (Observable(),
                (TransactionScope('name'),
                    (resourceManager,
                        (Resource(),)
                    ),
                )
            )
        body = be(dna)
        self.assertEquals(0, len(resourceManager.txs))
        list(compose(body.all.something()))
        self.assertEquals(0, len(resourceManager.txs))
        self.assertEquals(['something', 'commit'], [m.name for m in resourceTx.calledMethods])

    def testTransactionExceptionRollsbackTransaction(self):
        resourceTxs = []
        class Resource(object):
            def beginTransaction(self):
                resourceTx = CallTrace('resourceTx')
                resourceTxs.append(resourceTx)
                raise StopIteration(resourceTx)
                yield

        class CallTwoMethods(Observable):
            def twice(self, argument1, argument2):
                yield self.all.methodOne(argument1)
                self.ctx.tx.abort()
                yield self.all.methodTwo(argument2)

        dna = \
            (Observable(),
                (TransactionScope('name'),
                    (CallTwoMethods(),
                        (ResourceManager('name'),
                            (Resource(),),
                        )
                    )
                )
            )
        body = be(dna)
        list(compose(body.all.twice('one', 'two')))
        self.assertEquals(1, len(resourceTxs), resourceTxs)
        self.assertEquals(['methodOne', 'rollback'], [m.name for m in resourceTxs[0].calledMethods])

    def testTransactionLocals(self):
        tx = Transaction('name')
        tx.locals['myvar'] = 'value'
        self.assertEquals('value', tx.locals['myvar'])

    def testTransactionScopeName(self):
        scope = TransactionScope("name")
        self.assertEquals("name", scope._transactionName)

    def testTransactionYieldsCallablesInCommits(self):
        callable = lambda: None
        class Committer(Observable):
            def begin(inner, name):
                inner.ctx.tx.join(inner)
            def commit(inner, id):
                yield callable

        observable = Observable()
        scope = TransactionScope("name")
        observable.addObserver(scope)
        scope.addObserver(Committer())

        result = list(compose(observable.all.someMethod()))

        self.assertTrue(callable in result)


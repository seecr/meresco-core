## begin license ##
#
# "Meresco Core" is an open-source library containing components to build searchengines, repositories and archives.
#
# Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007 SURFnet. http://www.surfnet.nl
# Copyright (C) 2007-2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2011-2012, 2014, 2020-2021 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2011, 2020-2021 Stichting Kennisnet https://www.kennisnet.nl
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

from unittest import TestCase
from seecr.test import CallTrace
from weightless.core import NoneOfTheObserversRespond, DeclineMessage
from meresco.core import ResourceManager, TransactionScope, TransactionException, Transaction, Observable, Transparent

from weightless.core import compose, be

class TransactionTest(TestCase):

    def testTransaction_AllUnknowned(self):
        traces = []
        class AResource(object):
            class MyTransaction(object):
                def g(self):
                    traces.append('g')
                    return
                    yield
                def commit(self):
                    traces.append('commit')
                    return
                    yield
            def beginTransaction(self):
                traces.append('begin')
                return AResource.MyTransaction()
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
        self.assertEqual([], result)
        self.assertEqual(4, len(traces))
        self.assertEqual(['begin', 'g', 'g', 'commit'], traces)

    def testTransaction_DoUnknowned(self):
        traces = []
        class AResource(object):
            class MyTransaction(object):
                def g(self):
                    traces.append('g')
                def commit(self):
                    traces.append('commit')
                    return
                    yield
            def beginTransaction(self):
                traces.append('begin')
                return AResource.MyTransaction()
                yield

        class AllToDo(Observable):
            def add(self):
                self.do.f()
                return
                yield

        class InBetween(Observable):
            def f(self):
                self.do.g()

        dna = \
            (Observable(),
                (TransactionScope("transactionName"),
                    (AllToDo(),
                        (InBetween(),
                            (ResourceManager("transactionName"),
                                (AResource(),)
                            )
                        )
                    )
                )
            )
        body = be(dna)
        list(compose(body.all.add()))
        self.assertEqual(3, len(traces))
        self.assertEqual(['begin', 'g', 'commit'], traces)

    def testTransaction_CallUnknowned(self):
        traces = []
        class AResource(object):
            class MyTransaction(object):
                def g(self):
                    traces.append('g')
                    return 'retval'
                def commit(self):
                    traces.append('commit')
                    return
                    yield
            def beginTransaction(self):
                traces.append('begin')
                return AResource.MyTransaction()
                yield

        class AllToCall(Observable):
            def add(self):
                retval = self.call.f()
                yield retval

        class InBetween(Observable):
            def f(self):
                return self.call.g()

        dna = \
            (Observable(),
                (TransactionScope("transactionName"),
                    (AllToCall(),
                        (InBetween(),
                            (ResourceManager("transactionName"),
                                (AResource(),)
                            )
                        )
                    )
                )
            )
        body = be(dna)
        result = list(compose(body.all.add()))
        self.assertEqual(['retval'], result)
        self.assertEqual(3, len(traces))
        self.assertEqual(['begin', 'g', 'commit'], traces)

    def testTransaction_AnyUnknowned(self):
        traces = []
        class AResource(object):
            class MyTransaction(object):
                def g(self):
                    traces.append('g')
                    return 'MyTx.g'
                    yield
                def commit(self):
                    traces.append('commit')
                    return
                    yield
            def beginTransaction(self):
                traces.append('begin')
                return AResource.MyTransaction()
                yield

        class InBetween(Observable):
            def f(self):
                response = yield self.any.g()
                return response

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
        composed = compose(body.any.f())
        try:
            next(composed)
            self.fail("Should not come here")
        except StopIteration as e:
            self.assertEqual(('MyTx.g',), e.args)
        self.assertEqual(3, len(traces))
        self.assertEqual(['begin', 'g', 'commit'], traces)

    def testContinueOnNoneOfTheObserversRespond(self):
        class Responder(object):
            def __init__(self, value):
                self.value = value
            def call_unknown(self, message, *args, **kwargs):
                return self.value
            def any_unknown(self, message, *args, **kwargs):
                yield self.value
                return self.value

        class AResource(object):
            class MyTransaction(object):
                def commit(self):
                    return
                    yield
            def beginTransaction(self):
                return AResource.MyTransaction()
                yield

        dna = \
            (Observable(),
                (TransactionScope("transactionName"),
                    (ResourceManager("transactionName"),
                        (AResource(),)
                    ),
                ),
                (Responder(42),)
            )
        body = be(dna)
        self.assertEqual([42], list(compose(body.any.f())))

        dna = \
            (Observable(),
                (TransactionScope("transactionName"),
                    (ResourceManager("transactionName"),
                        (AResource(),)
                    ),
                    (Responder(42),)
                ),
            )
        body = be(dna)
        self.assertEqual([42], list(compose(body.any.f())))

        class Any2Call(Observable):
            def any_unknown(self, message, *args, **kwargs):
                try:
                    yield self.call.unknown(message, *args, **kwargs)
                except NoneOfTheObserversRespond:
                    raise DeclineMessage

        dna = \
            (Observable(),
                (TransactionScope("transactionName"),
                    (Any2Call(),
                        (ResourceManager("transactionName"),
                            (AResource(),)
                        ),
                        (Responder(42),)
                    )
                ),
            )
        body = be(dna)
        self.assertEqual([42], list(compose(body.any.f())))


    def testResourceManagerAllUnknown_asserts_NoResponse(self):
        # Exactly like Observable, but the Transaction objects
        # are no Observers, so the assertion had to be reimplemented here.
        class Resource(object):
            class NotAnObservable(object):
                def allLike(self):
                    yield 'allResult'

                def asyncAnyLike(self):
                    return 'anyResult'
                    yield

                def commit(self):
                    return
                    yield

            def beginTransaction(self):
                return Resource.NotAnObservable()
                yield

        dna = (Observable(),
            (TransactionScope('notImportantHere'),
                (ResourceManager('notImportantHere'),
                    (Resource(),),
                )
            )
        )
        server = be(dna)

        composed = compose(server.all.allLike())
        self.assertEqual(['allResult'], list(composed))

        composed = compose(server.all.asyncAnyLike())
        try:
            list(composed)
        except AssertionError as e:
            self.assertTrue("> returned 'anyResult'" in str(e), str(e))
        else:
            self.fail("Should not come here")

    def testResourceManagerHandlesAttributeError(self):
        class Resource(object):
            def beginTransaction(self):
                return object()
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
        self.assertEqual(1, len(commitCalled))
        self.assertEqual(tx.getId(), commitCalled[0])

    def testFreeTransaction(self):
        resourceManager = ResourceManager('name')
        resourceTx = CallTrace('resourceTx')
        class Resource(object):
            def beginTransaction(self):
                return resourceTx
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
        self.assertEqual(0, len(resourceManager.txs))
        list(compose(body.all.something()))
        self.assertEqual(0, len(resourceManager.txs))
        self.assertEqual(['something', 'commit'], [m.name for m in resourceTx.calledMethods])

    def testTransactionExceptionRollsbackTransaction(self):
        resourceTxs = []
        class Resource(object):
            def beginTransaction(self):
                resourceTx = CallTrace('resourceTx')
                resourceTxs.append(resourceTx)
                return resourceTx
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
        self.assertEqual(1, len(resourceTxs), resourceTxs)
        self.assertEqual(['methodOne', 'rollback'], [m.name for m in resourceTxs[0].calledMethods])

    def testTransactionLocals(self):
        tx = Transaction('name')
        tx.locals['myvar'] = 'value'
        self.assertEqual('value', tx.locals['myvar'])

    def testTransactionScopeName(self):
        scope = TransactionScope("name")
        self.assertEqual("name", scope._transactionName)

    def testTransactionYieldsCallablesInCommits(self):
        callable = lambda: None
        class Committer(Observable):
            def begin(inner, name):
                inner.ctx.tx.join(inner)
                return
                yield
            def commit(inner, id):
                yield callable

        observable = Observable()
        scope = TransactionScope("name")
        observable.addObserver(scope)
        scope.addObserver(Committer())

        result = list(compose(observable.all.someMethod()))

        self.assertTrue(callable in result)

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
        scope1 = compose(body.all.doSomething())
        scope2 = compose(body.all.doSomething())
        next(scope1)
        next(scope2)
        next(scope1)
        next(scope2)
        self.assertTrue(txId[0] != txId[1])
        self.assertTrue(txId[1] > 0)
        self.assertTrue(txId[0] > 0)
        self.assertEqual(txId[0], txId[2])
        self.assertEqual(txId[1], txId[3])

    def testTransactionCommit(self):
        collected = {}
        class MyFirstTxParticipant(Transparent):
            def begin(self, name):
                self.ctx.tx.join(self)
                return
                yield
            def doSomething(self):
                collected[self.ctx.tx.getId()] = ['first']
                yield self.any.doSomething()
            def commit(self, id):
                collected[id].append('done 1')
                return
                yield
        class MySecondTxParticipant(Observable):
            def begin(self, name):
                self.ctx.tx.join(self)
                return
                yield
            def doSomething(self):
                collected[self.ctx.tx.getId()].append('second')
                yield 'second'
            def commit(self, id):
                collected[id].append('done 2')
                return
                yield
        dna = \
            (Observable(),
                (TransactionScope('name'),
                    (MyFirstTxParticipant(),
                        (MySecondTxParticipant(),)
                    )
                )
            )
        body = be(dna)
        list(compose(body.all.doSomething()))
        self.assertEqual(['first', 'second', 'done 1', 'done 2'], list(collected.values())[0])

    def testTransactionScopeObservableName(self):
        self.assertEqual('name', TransactionScope('name').observable_name())
        self.assertEqual('name', TransactionScope(transactionName='name').observable_name())
        self.assertEqual('name', TransactionScope(transactionName='transaction', name='name').observable_name())

    def testObjectScope(self):
        o1 = object()
        tx = Transaction('transactionScopeName')
        tx.objectScope(o1)['key'] = 'value'
        self.assertEqual({'key': 'value'}, tx.objectScope(o1))
        o2 = object()
        self.assertEqual({}, tx.objectScope(o2))


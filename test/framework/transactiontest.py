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

from cq2utils import CallTrace
from unittest import TestCase
from merescocore.framework import ResourceManager, be, Observable, compose, TransactionScope, TransactionException, Transaction

class TransactionTest(TestCase):
    def testOne(self):
        traces = []
        def factoryMethod(tx):
            trace = CallTrace('transaction')
            traces.append(trace)
            return trace

        class CallTwoMethods(Observable):
            def twice(self, argument1, argument2):
                yield self.all.methodOne(argument1)
                yield self.all.methodTwo(argument2)

        dna = \
            (Observable(),
                (TransactionScope("transactionName"),
                    (CallTwoMethods(),
                        (ResourceManager("transactionName", factoryMethod),)
                    )
                )
            )
        body = be(dna)

        list(compose(body.all.twice('one', 'two')))

        self.assertEquals(1, len(traces))
        self.assertEquals(['methodOne', 'methodTwo', 'commit'], [m.name for m in traces[0].calledMethods])

    def testResourceManagerHandlesAttributeError(self):
        class ResourceTransaction(object):
            def __init__(self, tx):
                pass
        txfactory = ResourceManager('transaction', ResourceTransaction)
        __callstack_var_tx__ = CallTrace('TransactionScope')
        txfactory.begin()
        try:
            txfactory.unknown('doesnotexist')
        except AttributeError:
            self.fail('ResourceManager must ignore unknown methods.')

    def testJoinOnlyOnce(self):
        commitCalled = []
        class MockResource(object):
            def commit(self):
                commitCalled.append(1)
        tx = Transaction('name')
        resource = MockResource()
        tx.join(resource)
        tx.join(resource)
        tx.commit()
        self.assertEquals(1, len(commitCalled))

    def testFreeTransaction(self):
        resourceManager = ResourceManager('name', lambda resourceManager: CallTrace())
        dna = \
            (Observable(),
                (TransactionScope('name'),
                    (resourceManager,)
                )
            )
        body = be(dna)
        self.assertEquals(0, len(resourceManager.txs))
        body.do.something()
        self.assertEquals(0, len(resourceManager.txs))

    def testTransactionExceptionRollsbackTransaction(self):
        resourceTxs = []
        def factoryMethod(tx):
            resourceTx = CallTrace('resourceTx')
            resourceTxs.append(resourceTx)
            return resourceTx

        class CallTwoMethods(Observable):
            def twice(self, argument1, argument2):
                yield self.all.methodOne(argument1)
                self.tx.abort()
                yield self.all.methodTwo(argument2)

        dna = \
            (Observable(),
                (TransactionScope('name'),
                    (CallTwoMethods(),
                        (ResourceManager('name', factoryMethod),)
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

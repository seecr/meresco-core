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

from cq2utils import CallTrace
from unittest import TestCase
from meresco.framework import TransactionFactory, be, Observable, compose, TransactionScope

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
                (TransactionScope(),
                    (CallTwoMethods(),
                        (TransactionFactory(factoryMethod),)
                    )
                )
            )
        body = be(dna)

        list(compose(body.all.twice('one', 'two')))

        self.assertEquals(1, len(traces))
        self.assertEquals(3, len(traces[0].calledMethods))
        self.assertEquals(['methodOne', 'methodTwo', 'finalize'], [m.name for m in traces[0].calledMethods])

    def testTransactionFactoryHandlesAttributeError(self):
        methodsCalled = []
        class Mock(object):
            def finalize(self):
                methodsCalled.append('finalize')
            def exists(self):
                methodsCalled.append('exists')

        factory = TransactionFactory(lambda tx: Mock())
        __callstack_var_tx__ = CallTrace('Transaction')
        observable = Observable()
        observable.addObserver(factory)
        observable.once.begin()
        list(observable.all.exists())
        observable.once.commit()

        self.assertEquals(['exists', 'finalize'], methodsCalled)

        methodsCalled = []

        observable.once.begin()
        list(observable.all.doesNotExist())
        observable.once.commit()

        self.assertEquals(['finalize'], methodsCalled)





        

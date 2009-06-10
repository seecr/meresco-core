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
from cq2utils import CQ2TestCase, CallTrace
from merescocore.framework import BatchTransactionScope, Observable
from callstackscope import callstackscope

class BatchTransactionScopeTest(CQ2TestCase):
    def testOne(self):
        observer = CallTrace("observer")

        batchTransactionScope = BatchTransactionScope("batch", reactor=CallTrace("reactor"))
        batchTransactionScope.addObserver(observer)

        observable = Observable()
        observable.addObserver(batchTransactionScope)

        observable.do.exoticMethod()

        self.assertEquals(["begin", "exoticMethod"], [m.name for m in observer.calledMethods])

        
    def testBatchSize1(self):
        observable = Observable()
        batch = BatchTransactionScope("batch", reactor=CallTrace("reactor"), batchSize=1, timeout=99999999)
        observer = CallTrace('observer')
        committer = CallTrace("committer")
        def begin():
            tx = callstackscope('__callstack_var_tx__')
            tx.join(committer)
        observer.begin = begin
        observable.addObserver(batch)
        batch.addObserver(observer)

        observable.do.addDocument("aDocument")

        self.assertEquals(["addDocument"], [m.name for m in observer.calledMethods])
        self.assertEquals(['commit'], [m.name for m in committer.calledMethods])

    def testBatched(self):
        observable = Observable()
        batch = BatchTransactionScope("batch", reactor=CallTrace("reactor"), batchSize=2, timeout=99999999)
        observer = CallTrace('observer')
        committer = CallTrace("committer")
        def begin():
            tx = callstackscope('__callstack_var_tx__')
            tx.join(committer)
        observer.methods['begin'] = begin
        observable.addObserver(batch)
        batch.addObserver(observer)

        observable.do.addDocument("aDocument")

        self.assertEquals(['begin', "addDocument"], [m.name for m in observer.calledMethods])
        self.assertEquals([], [m.name for m in committer.calledMethods])

        observable.do.addDocument("aDocument")

        self.assertEquals(['begin', "addDocument", "addDocument"], [m.name for m in observer.calledMethods])
        self.assertEquals(["commit"], [m.name for m in committer.calledMethods])
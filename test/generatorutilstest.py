## begin license ##
# 
# "Meresco Core" is an open-source library containing components to build searchengines, repositories and archives. 
# 
# Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007 SURFnet. http://www.surfnet.nl
# Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2011-2012 Seecr (Seek You Too B.V.) http://seecr.nl
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

from unittest import TestCase, main

from meresco.core.generatorutils import decorate, decorateWith, asyncreturn

class GeneratorUtilsTest(TestCase):

    def testAlternativePeekNotEmpty(self):
        result = list(decorate(1, (i for i in [2]), 3))
        self.assertEquals([1,2,3], result)

    def testAlternativePeekEmpty(self):
        result = list(decorate(1, (i for i in []), 3))
        self.assertEquals([], result)

    def testDecorateWith(self):
        def gen(yieldSomething=True):
            if yieldSomething :
                yield 'something'
        self.assertEquals("something", "".join(gen()))
        self.assertEquals("", "".join(gen(yieldSomething=False)))

        @decorateWith("This is ", ", isn't it?")
        def tobedecorated1(*args, **kwargs):
            return gen(*args, **kwargs)
        self.assertEquals("This is something, isn't it?", "".join(tobedecorated1()))
        self.assertEquals("", "".join(tobedecorated1(yieldSomething=False)))

    def testAsyncreturn(self):
        @asyncreturn
        def f():
            return 5
        
        class A(object):
            @asyncreturn
            def meth(self):
                return 5

            @classmethod
            @asyncreturn
            def classMeth(cls):
                return 5

            @staticmethod
            @asyncreturn
            def staticMeth():
                return 5

        try: f().next()
        except StopIteration, e: self.assertEquals((5,), e.args)
        else: self.fail('Should not happen.')

        try: A().meth().next()
        except StopIteration, e: self.assertEquals((5,), e.args)
        else: self.fail('Should not happen.')

        try: A.classMeth().next()
        except StopIteration, e: self.assertEquals((5,), e.args)
        else: self.fail('Should not happen.')

        try: A.staticMeth().next()
        except StopIteration, e: self.assertEquals((5,), e.args)
        else: self.fail('Should not happen.')

    def testAsyncreturnFailsOnGenerator(self):
        @asyncreturn
        def f():
            yield
        
        try:
            f().next()
        except AssertionError, e:
            self.assertEquals('Only use for non-generators.', str(e))
        else:
            self.fail('Should not happen.')


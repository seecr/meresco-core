## begin license ##
#
# "Meresco Core" is an open-source library containing components to build searchengines, repositories and archives.
#
# Copyright (C) 2011-2012, 2014 Seecr (Seek You Too B.V.) http://seecr.nl
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

from meresco.core import Observable, Transparent

from weightless.core import compose, be

class ObservableTest(TestCase):
    def testResolveCallStackVariables(self):
        do_result = []
        call_result = []
        class StackVarHolder(Observable):
            def all_unknown(self, message, *args, **kwargs):
                __callstack_var_myvar__ = []
                yield self.all.unknown(message, *args, **kwargs)
                yield __callstack_var_myvar__

            def any_unknown(self, message, *args, **kwargs):
                __callstack_var_myvar__ = []
                yield self.any.unknown(message, *args, **kwargs)
                raise StopIteration(__callstack_var_myvar__)

            def call_unknown(self, message, *args, **kwargs):
                __callstack_var_myvar__ = []
                call_result.append(__callstack_var_myvar__)
                return self.call.unknown(message, *args, **kwargs)

            def do_unknown(self, message, *args, **kwargs):
                __callstack_var_myvar__ = []
                do_result.append(__callstack_var_myvar__)
                self.do.unknown(message, *args, **kwargs)

        class StackVarUser(Observable):
            def useVariableAll(self):
                self.ctx.myvar.append('Thingy')
                yield 'stuffed'

            def useVariableAny(self):
                self.ctx.myvar.append('Thingy')
                return
                yield

            def useVariableCall(self):
                self.ctx.myvar.append('Thingy')
                return 'called'

            def useVariableDo(self):
                self.ctx.myvar.append('Thingy')

        dna = \
            (Observable(),
                (StackVarHolder(),
                    (Transparent(),
                        (StackVarUser(),)
                    )
                )
            )
        root = be(dna)
        self.assertEquals(['stuffed', ['Thingy']], list(compose(root.all.useVariableAll())))

        composed = compose(root.any.useVariableAny())
        try:
            while True:
                next(composed)
        except StopIteration as e:
            self.assertEquals((['Thingy'],), e.args)

        self.assertEquals('called', root.call.useVariableCall())
        self.assertEquals([['Thingy']], call_result)

        self.assertEquals(None, root.do.useVariableDo())
        self.assertEquals([['Thingy']], do_result)


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
from sys import exc_info
from weightless.core import compose, local

class Defer(object):
    def __init__(self, observers, defereeType):
        self._observers = observers
        self._defereeType = defereeType

    def __getattr__(self, attr):
        return self._defereeType(self._observers, attr)

    def __getitem__(self, target):
        return Defer([o for o in self._observers if hasattr(o, "observable_name") and o.observable_name() == target], self._defereeType)

    def unknown(self, message, *args, **kwargs):
        try:
            return getattr(self, message)(*args, **kwargs)
        except:
            exType, exValue, exTraceback = exc_info()
            raise exType, exValue, exTraceback.tb_next # skip myself from traceback

class DeferredMessage(object):
    def __init__(self, observers, message):
        self._observers = observers
        self._message = message

    def __call__(self, *args, **kwargs):
        return self._gatherResponses(*args, **kwargs)

    def _gatherResponses(self, *args, **kwargs):
        #from sys import stdout
        for observer in self._observers:
            if hasattr(observer, self._message):
                try:
                    answer = getattr(observer, self._message)(*args, **kwargs)
                    #print '!!known->answer: type(answer), answer: %s, %s' % (type(answer), answer)
                    #from weightless.core.compose import tostring
                    #print '>>>START\n', tostring(answer)
                    #print '<<<END'
                    #stdout.flush()
                    shouldBeNone = yield answer
                    #assert shouldBeNone is None, 'DeferredMessage._gatherResponses() shouldBeNone is: %s' % shouldBeNone
                    if shouldBeNone is not None:
                        raise StopIteration(shouldBeNone)
                except:
                    exType, exValue, exTraceback = exc_info()
                    raise exType, exValue, exTraceback.tb_next # skip myself from traceback
                finally:
                    answer = None
            elif hasattr(observer, 'unknown'):
                try:
                    responses = getattr(observer, 'unknown')(self._message, *args, **kwargs)
                    #print 'FIX ME !!!!'
                    #stdout.flush()
                except TypeError, e:
                    raise TypeError(str(e) + ' on ' + str(observer))
                if responses:
                    try:
                        #print 'unknown->responses: type(responses), responses: %s, %s' % (type(responses), responses)
                        #from weightless.core.compose import tostring
                        #print '>>>START\n', tostring(responses)
                        #print '<<<END'
                        #stdout.flush()
                        shouldBeNone = yield responses
                        if shouldBeNone is not None:
                            raise StopIteration(shouldBeNone)
                    except:
                        exType, exValue, exTraceback = exc_info()
                        raise exType, exValue, exTraceback.tb_next # skip myself from traceback
                    finally:
                        responses.close()# avoid cycles, see http://www.python.org/dev/peps/pep-0342/
                        responses = None # avoid cycles, see http://www.python.org/dev/peps/pep-0342/

class AllMessage(DeferredMessage):
    def __call__(self, *args, **kwargs):
        return compose(self._gatherResponses(*args, **kwargs))

class AnyMessage(DeferredMessage):
    def __call__(self, *args, **kwargs):
        try:
            results = DeferredMessage.__call__(self, *args, **kwargs)
            return results.next()
        except StopIteration:
            raise AttributeError('None of the %d observers responds to any.%s(...)' % (len(self._observers), self._message))
        except:
            exType, exValue, exTraceback = exc_info()
            raise exType, exValue, exTraceback.tb_next # skip myself from traceback
        finally:
            results.close()
            results = None

class DoMessage(DeferredMessage):
    def __call__(self, *args, **kwargs):
        try:
            for ignore in compose(DeferredMessage.__call__(self, *args, **kwargs)):
                pass
        except:
            exType, exValue, exTraceback = exc_info()
            raise exType, exValue, exTraceback.tb_next # skip myself from traceback

class AsyncdoMessage(DeferredMessage):
    def __call__(self, *args, **kwargs):
        try:
            for value in compose(DeferredMessage.__call__(self, *args, **kwargs)):
                if callable(value):
                    yield value
        except:
            exType, exValue, exTraceback = exc_info()
            raise exType, exValue, exTraceback.tb_next # skip myself from traceback

class AsyncanyMessage(DeferredMessage):
    def __call__(self, *args, **kwargs):
        try:
            result = DeferredMessage.__call__(self, *args, **kwargs)
            m = None
            while True:
                r = result.send(m) 
                m = yield r
                if not callable(m):
                    raise StopIteration(m)
        except StopIteration, e:
            if e.args:
                raise
            raise AttributeError('None of the %d observers responds to asyncany.%s(...)' % (len(self._observers), self._message))

class OnceMessage(DeferredMessage):
    def __call__(self, *args, **kwargs):
        done = set()
        return self._callonce(self._observers, args, kwargs, done)

    def _callonce(self, observers, args, kwargs, done):
        for observer in observers:
            if observer not in done:
                done.add(observer)
                if hasattr(observer, self._message):
                    getattr(observer, self._message)(*args, **kwargs)
                if isinstance(observer, Observable):
                    self._callonce(observer._observers, args, kwargs, done)

def be(strand):
    helicesDone = set()
    return _beRecursive(strand, helicesDone)

def _beRecursive(helix, helicesDone):
    if callable(helix):
        helix = helix(helicesDone)
    component = helix[0]
    strand = helix[1:]
    if not helix in helicesDone and strand:
        component.addStrand(strand, helicesDone)
        helicesDone.add(helix)
    return component

class Context(object):
    def __getattr__(self, name):
        try:
            return local('__callstack_var_%s__' % name)
        except AttributeError:
            raise AttributeError("'%s' has no attribute '%s'" % (self, name))


class Observable(object):
    def __init__(self, name = None):
        self._observers = []
        self.all = Defer(self._observers, AllMessage)
        self.any = Defer(self._observers, AnyMessage)
        self.do = Defer(self._observers, DoMessage)
        self.asyncdo = Defer(self._observers, AsyncdoMessage)
        self.asyncany = Defer(self._observers, AsyncanyMessage)
        self.once = Defer(self._observers, OnceMessage)
        self._name = name

        self.ctx = Context()
    
    def observable_name(self):
        return self._name

    def observable_setName(self, name):
        self._name = name
        return self

    def addObserver(self, observer):
        self._observers.append(observer)

    def addStrand(self, strand, helicesDone):
        for helix in strand:
            self.addObserver(_beRecursive(helix, helicesDone))

    def printTree(self, depth=0):
        def printInColor(ident, color, text):
            print ' '*ident, chr(27)+"[0;" + str(color) + "m", text, chr(27)+"[0m"
        print ' ' * depth, self.__repr__()
        for observer in self._observers:
            if hasattr(observer, 'printTree'):
                observer.printTree(depth=depth+1)
            else:
                printInColor(depth+1, 31, observer)

    def __repr__(self):
        return "%s(name=%s)" % (self.__class__.__name__, repr(self._name))

class Transparant(Observable):
    def unknown(self, message, *args, **kwargs):
        return self.all.unknown(message, *args, **kwargs)

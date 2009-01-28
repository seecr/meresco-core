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
from sys import exc_info
from generatorutils import compose
from inspect import currentframe

class Defer:
    def __init__(self, observable, defereeType):
        self._observable = observable
        self._defereeType = defereeType

    def __getattr__(self, attr):
        return self._defereeType(self._observable._observers, attr)

    def unknown(self, message, *args, **kwargs):
        try:
            return getattr(self, message)(*args, **kwargs)
        except:
            exType, exValue, exTraceback = exc_info()
            raise exType, exValue, exTraceback.tb_next # skip myself from traceback

class DeferredMessage:
    def __init__(self, observers, message):
        self._observers = observers
        self._message = message

    def __call__(self, *args, **kwargs):
        return self._gatherResponses(*args, **kwargs)

    def _gatherResponses(self, *args, **kwargs):
        for observer in self._observers:
            if hasattr(observer, self._message):
                try:
                    yield getattr(observer, self._message)(*args, **kwargs)
                except:
                    exType, exValue, exTraceback = exc_info()
                    raise exType, exValue, exTraceback.tb_next # skip myself from traceback
            elif hasattr(observer, 'unknown'):
                try:
                    responses = getattr(observer, 'unknown')(self._message, *args, **kwargs)
                except TypeError, e:
                    raise TypeError(str(e) + ' on ' + str(observer))
                if responses:
                    try:
                        for response in responses:
                            yield response
                    except:
                        exType, exValue, exTraceback = exc_info()
                        raise exType, exValue, exTraceback.tb_next # skip myself from traceback

class AllMessage(DeferredMessage):
    def __call__(self, *args, **kwargs):
        return compose(self._gatherResponses(*args, **kwargs))

class AnyMessage(DeferredMessage):
    def __call__(self, *args, **kwargs):
        try:
            return DeferredMessage.__call__(self, *args, **kwargs).next()
        except StopIteration:
            raise AttributeError('None of the %d observers responds to any.%s(...)' % (len(self._observers), self._message))
        except:
            exType, exValue, exTraceback = exc_info()
            raise exType, exValue, exTraceback.tb_next # skip myself from traceback

class DoMessage(DeferredMessage):
    def __call__(self, *args, **kwargs):
        try:
            for ignore in compose(DeferredMessage.__call__(self, *args, **kwargs)):
                pass
        except:
            exType, exValue, exTraceback = exc_info()
            raise exType, exValue, exTraceback.tb_next # skip myself from traceback


class OnceMessage(DeferredMessage):

    def __call__(self, *args, **kwargs):
        done = []
        return self._callonce(self._observers, args, kwargs, done)

    def _callonce(self, observers, args, kwargs, done):
        for observer in observers:
            if hasattr(observer, self._message) and observer not in done:
                getattr(observer, self._message)(*args, **kwargs)
                done.append(observer)
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

def _getCallstackVar(name):
    stackVarName = '__callstack_var_%s__' % name
    frame = currentframe().f_back
    while stackVarName not in frame.f_locals:
        frame = frame.f_back
    return frame.f_locals[stackVarName]

def getCallstackVar(name):
    try:
        return _getCallstackVar(name)
    except AttributeError:
        raise AttributeError("Callstack variable '%s' not found." % name)

class Observable(object):
    def __init__(self, name = None):
        self._observers = []
        self.all = Defer(self, AllMessage)
        self.any = Defer(self, AnyMessage)
        self.do = Defer(self, DoMessage)
        self.once = Defer(self, OnceMessage)
        if name:
            self.__repr__ = lambda: name

    def __getattr__(self, name):
        try:
            return _getCallstackVar(name)
        except AttributeError:
            raise AttributeError("'%s' has no attribute '%s'" % (self, name))

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

class Transparant(Observable):
    def unknown(self, message, *args, **kwargs):
        return self.all.unknown(message, *args, **kwargs)

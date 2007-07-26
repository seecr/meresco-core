## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) SURF Foundation. http://www.surf.nl
#    Copyright (C) Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) SURFnet. http://www.surfnet.nl
#    Copyright (C) Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
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

class Defer:
    def __init__(self, observable, defereeType):
        self._observable = observable
        self._defereeType = defereeType

    def __getattr__(self, attr):
        return self._defereeType(self._observable._observers, attr)

    def unknown(self, message, *args, **kwargs):
        return getattr(self, message)(*args, **kwargs)

class DeferredMessage:
    def __init__(self, observers, message):
        self._observers = observers
        self._message = message

    def __call__(self, *args, **kwargs):
        for observer in self._observers:
            if hasattr(observer, self._message):
                yield getattr(observer, self._message)(*args, **kwargs)
            elif hasattr(observer, 'unknown'):
                responses = getattr(observer, 'unknown')(self._message, *args, **kwargs)
                if responses:
                    for response in responses:
                        yield response

class AllMessage(DeferredMessage):
    pass

class AnyMessage(DeferredMessage):
    def __call__(self, *args, **kwargs):
        try:
            return DeferredMessage.__call__(self, *args, **kwargs).next()
        except StopIteration:
            raise AttributeError('None of the %d observers responds to any.%s(...)' % (len(self._observers), self._message))

class DoMessage(DeferredMessage):
    def __call__(self, *args, **kwargs):
        for ignore in DeferredMessage.__call__(self, *args, **kwargs):
            pass

class Observable(object):
    def __init__(self, name = None):
        self._observers = []
        self.all = Defer(self, AllMessage)
        self.any = Defer(self, AnyMessage)
        self.do = Defer(self, DoMessage)
        if name:
            self.__repr__ = lambda: name

    def addObserver(self, observer):
        self._observers.append(observer)

    def addObservers(self, tree):
        for node in tree:
            if isinstance(node, tuple):
                node, branch = node
                node.addObservers(branch)
            self.addObserver(node)

    def _notifyObservers(self, __returnResult__, *args, **kwargs):
        """deprecated"""
        i = 0
        while i < len(self._observers):
            result = self._observers[i].notify(*args, **kwargs)
            if __returnResult__ and result != None:
                return result
            i += 1

    def changed(self, *args, **kwargs):
        """deprecated"""
        return self._notifyObservers(False, *args, **kwargs)

    def process(self, *args, **kwargs):
        """deprecated"""
        return self._notifyObservers(True, *args, **kwargs)

class Function:

    def __init__(self, observable):
        self._observable = observable
        self._observable.addObserver(self)

    def notify(self, *args, **kwargs):
        self._result = args #kwargs is nog een vraagteken voor mij (KVS)
        if len(self._result) == 0:
            self._result = None
        elif len(self._result) == 1:
            self._result = self._result[0]

    def __call__(self, *args, **kwargs):
        self._observable.notify(*args, **kwargs) # hier is **kwargs triviaal
        return self._result

class FunctionObservable(Observable):
    #ik weet het, YAGNI, maar het is zooooo mooi symmetrisch - wilde toch even laten zien dat dit het soort dingen is wat we kunnen doen en denk dat we het nut vrij snel tegenkomen. Zo niet dan mag hij in het vuilnisvat

    def __init__(self, function):
        Observable.__init__(self)
        self._function = function

    def notify(self, *args, **kwargs):
        results = self._function(*args, **kwargs)
        self.changed(*results)

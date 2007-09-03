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
from sys import exc_info
from generatorutils import compose

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
        for observer in self._observers:
            if hasattr(observer, self._message):
                try:
                    yield getattr(observer, self._message)(*args, **kwargs)
                except:
                    exType, exValue, exTraceback = exc_info()
                    raise exType, exValue, exTraceback.tb_next # skip myself from traceback
            elif hasattr(observer, 'unknown'):
                responses = getattr(observer, 'unknown')(self._message, *args, **kwargs)
                if responses:
                    try:
                        for response in responses:
                            yield response
                    except:
                        exType, exValue, exTraceback = exc_info()
                        raise exType, exValue, exTraceback.tb_next # skip myself from traceback

class AllMessage(DeferredMessage):
    pass

class AnyMessage(DeferredMessage):
    def __call__(self, *args, **kwargs):
        try:
            return compose(DeferredMessage.__call__(self, *args, **kwargs)).next()
        except StopIteration:
            raise AttributeError('None of the %d observers responds to any.%s(...)' % (len(self._observers), self._message))
        except:
            exType, exValue, exTraceback = exc_info()
            raise exType, exValue, exTraceback.tb_next.tb_next # skip myself and compose from traceback

class DoMessage(DeferredMessage):
    def __call__(self, *args, **kwargs):
        try:
            for ignore in compose(DeferredMessage.__call__(self, *args, **kwargs)):
                pass
        except:
            exType, exValue, exTraceback = exc_info()
            raise exType, exValue, exTraceback.tb_next.tb_next # skip myself and compose from traceback


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

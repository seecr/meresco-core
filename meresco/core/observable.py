
from weightless.core import Observable as Observable_orig, Transparent as Transparent_orig, local


class Context(object):
    def __getattr__(self, name):
        try:
            return local('__callstack_var_%s__' % name)
        except AttributeError:
            raise AttributeError("'%s' has no attribute '%s'" % (self, name))


class Observable(Observable_orig):
    def __init__(self, name=None):
        Observable_orig.__init__(self, name=name)
        self.ctx = Context()


class Transparent(Transparent_orig):
    def __init__(self, name=None):
        Transparent_orig.__init__(self, name=name)
        self.ctx = Context()


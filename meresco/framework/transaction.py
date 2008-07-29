from meresco.framework import Observable
from inspect import currentframe
from functools import partial as curry

def currentTransaction():
    frame = currentframe().f_back
    while '__tx__' not in frame.f_locals:
        frame = frame.f_back
    return frame.f_locals['__tx__']

class TxManager(object):

    def __getattr__(self, name):
        if name == 'values':
            return currentTransaction()['values']
        return getattr(object, name)

    def getId(self):
        return id(currentTransaction())


txManager = TxManager()

class TransactionScope(Observable):

    def _setTx(self, observer):
        observer.tx = txManager
        return observer

    def addObserver(self, observer):
        Observable.addObserver(self, self._setTx(observer))

    def _setTxOnDna(self, dna):
        for node in dna:
            if type(node) == tuple:
                node, branch = node
                yield self._setTx(node), self._setTxOnDna(branch)
            else:
                yield self._setTx(node)

    def addObservers(self, dna):
        return Observable.addObservers(self, self._setTxOnDna(dna))

    def unknown(self, name, *args, **kwargs):
        __tx__ = {'values': {}}
        for result in self.all.unknown(name, *args, **kwargs):
            yield result
        self.do.commit()


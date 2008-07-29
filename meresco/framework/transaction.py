from meresco.framework import Observable
from inspect import currentframe

def currentTransaction():
    frame = currentframe().f_back
    while '__tx__' not in frame.f_locals:
        frame = frame.f_back
    return frame.f_locals['__tx__']

class TransactionScope(Observable):
    def unknown(self, name, *args, **kwargs):
        __tx__ = {'values': {}}
        for result in self.all.unknown(name, *args, **kwargs):
            yield result
        self.do.commit()
    
class TxManager(object):

    def __getattr__(self, name):
        if name == 'values':
            return currentTransaction()['values']
        return getattr(object, name)
    
    def getId(self):
        return id(currentTransaction())
    
class TxParticipant(object):
    def __init__(self):
        self.tx = TxManager()


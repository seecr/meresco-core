from meresco.framework import Observable

class Transaction(object):

    def getId(self):
        return id(self)

class TransactionScope(Observable):

    def unknown(self, name, *args, **kwargs):
        __callstack_var_tx__ = Transaction()
        self.once.begin()
        for result in self.all.unknown(name, *args, **kwargs):
            yield result
        self.once.commit()


from meresco.framework.observable import Observable

class DictIdentity(object):
    
    def fieldsForField(self, documentField):
        yield documentField
        
class Identity(Observable): #is dat nodig?
    
    def unknown(self, oneArg):
        return oneArg
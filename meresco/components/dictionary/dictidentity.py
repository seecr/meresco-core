from meresco.framework.observable import Observable

class DictIdentity(object):
    
    def fieldsForField(self, documentField):
        yield documentField
        

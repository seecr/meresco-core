
class ContextSet:
    def __init__(self, name, aStream):
        self.name = name
        self._dictionary = {}
        self._reverseDictionary = {}
        self._readStream(aStream)
        
    def _readStream(self, aStream):
        for k,v in [line.strip().split('\t') for line in aStream]:
            if k not in self._dictionary:
                self._dictionary[k] = v
            if v not in self._reverseDictionary:
                self._reverseDictionary[v] = k
            
    def match(self, field):
        return '.' in field and field.split('.',1)[0] == self.name and field.split('.',1)[1] in self._dictionary
    
    def reverseMatch(self, field):
        return field in self._reverseDictionary
            
    def lookup(self, field):
        if not self.match(field):
            return field
        return self._dictionary[field.split('.',1)[1]]
        
    def reverseLookup(self, field):
        if not self.reverseMatch(field):
            return field
        return self.name + '.' + self._reverseDictionary[field]
    
class ContextSetException(Exception):
    pass

class ContextSetList:
    def __init__(self):
        self._contextsets = {}
        
    def lookup(self, field):
        if '.' not in field:
            return field
        context = field.split('.')[0]
        if context not in self._contextsets:
            raise ContextSetException('Unsupported contextset: ' + context)
        set = self._contextsets[context]
        if set.match(field):
            return set.lookup(field)
        raise ContextSetException('Unknown field: ' + field)
    
    def reverseLookup(self, field):
        for set in self._contextsets.values():
            if set.reverseMatch(field):
                return set.reverseLookup(field)
        return field
    
    def add(self, contextSet):
        self._contextsets[contextSet.name] = contextSet

class DocumentDict(object):
    def __init__(self):
        self._dict = {}

    def add(self, key, value):
        self.addField(DocumentField(key, value))

    def addField(self, documentField):
        fields = self.get(documentField.key)
        fields.append(documentField)
        self._dict[documentField.key] = fields

    def get(self, key):
        return self._dict.get(key, [])

    def __iter__(self):
        for fields in self._dict.itervalues():
            for documentField in fields:
                yield documentField

class DocumentField(object):

    def __init__(self, key, value, **kwargs):
        self.key = key
        self.value = value
        self.options = kwargs

    def __eq__(self, other):
        return type(other) == DocumentField and \
            self.key == other.key and \
            self.value == other.value and \
            self.options == other.options
            
    def __hash__(self):
        return hash(self.key)

    def __repr__(self):
        return '(%s => %s)' % (repr(self.key), repr(self.value))

def asDict(documentDict):
    result = {}
    for documentField in documentDict:
        value = result.get(documentField.key, [])
        value.append(documentField.value)
        result[documentField.key] = value
    return result

def fromDict(aDictionary):
    result = DocumentDict()
    for key,valueList in aDictionary.items():
        for value in valueList:
            result.add(key,value)
    return result
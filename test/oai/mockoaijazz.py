class MockOaiJazz:
    def __init__(self, selectAnswer = [], setsAnswer = [], deleted=[], isAvailableDefault=(True,True), isAvailableAnswer=[]):
        self._selectAnswer = selectAnswer
        self._setsAnswer = setsAnswer
        self._deleted = deleted
        self._isAvailableDefault = isAvailableDefault
        self._isAvailableAnswer = isAvailableAnswer
        self.oaiSelectArguments = {}

    def oaiSelect(self, *args, **kwargs):
        self.oaiSelectArguments = args
        return self._selectAnswer

    def getUnique(self, id):
        return 'Unique for test'

    def getSets(self, id):
        return self._setsAnswer

    def getDatestamp(self, id):
        return 'DATESTAMP_FOR_TEST'

    def getParts(self, id):
        raise "STOP"

    def isDeleted(self, id):
        return id in self._deleted

    def getAllPrefixes(self):
        return [('oai_dc',None,None)]

    def write(self, sink, id, partName):
        if partName == 'oai_dc':
            sink.write('<some:recorddata xmlns:some="http://some.example.org" id="%s"/>' % id.replace('&', '&amp;'))
        elif partName == '__stamp__':
            sink.write("""<__stamp__>
    <datestamp>DATESTAMP_FOR_TEST</datestamp>
</__stamp__>""")
        elif partName == '__sets__':
            sink.write("""<__sets__><set><setSpec>one:two:three</setSpec><setName>Three Piggies</setName></set><set><setSpec>one:two:four</setSpec><setName>Four Chickies</setName></set></__sets__>""")
        else:
            self.fail(partName + ' is unexpected')

    def isAvailable(self, id, partName):
        result = self._isAvailableDefault
        for (aId, aPartname, answer) in self._isAvailableAnswer:
            if (aId == None or aId == id) and aPartname == partName:
                result = answer
                break
        return result

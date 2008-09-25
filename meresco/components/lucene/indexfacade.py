
class AddCommand(object):

    def __init__(self, index, document):
        self.index = index
        self.document = document

    def __call__(self):
        self.index.addDocument(self.document)

    def __eq__(self, other):
        return other == self.document.identifier

class DeleteCommand(object):

    def __init__(self, index, anId):
        self.index = index
        self.anId = anId

    def __call__(self):
        self.index.delete(self.anId)


class IndexFacade(object):
    def __init__(self, index):
        self._queue = []
        self.index = index

    def addDocument(self, document):
        self._queue.append(AddCommand(self.index, document))

    def delete(self, anId):
        if anId in self._queue:
            self._queue.remove(anId)
        else:
            self._queue.append(DeleteCommand(self.index, anId))

    def executeQuery(self, query):
        return self.index.executeQuery(query)

    def flush(self):
        for command in self._queue:
            command()
        self.index._reopenIndex()
        self._queue = []
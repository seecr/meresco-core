
class Fields2OaiRecordTx(object):
    def __init__(self, resourceManager):
        self.resourceManager = resourceManager
        self._sets = set()
        self._metadataFormats = set()

    def addField(self, name, value):
        if name == 'set':
            self._sets.add(value)
        elif name == 'metadataFormat':
            self._metadataFormats.add(value)

    def commit(self):
        if self._metadataFormats:
            identifier = self.resourceManager.tx.locals['id']
            self.resourceManager.do.addOaiRecord(identifier=identifier, sets=self._sets, metadataFormats = self._metadataFormats)

    def rollback(self):
        pass

ADD = 1
DELETE = 2

QUEUE_NODES_LENGTH = 100

class DocumentQueue(object):
    
    def __init__(self, storageComponent, sink, reactor, frequency):
        self._storageComponent = storageComponent
        self._sink = sink
        self._reactor = reactor
        self._frequency = frequency
        self._queues = []
        self._token = self._reactor.addTimer(self._frequency, self._tick)
    
    def add(self, id, partname, document):
        self._storageComponent.add(id, partname, document)
        self._enqueue((ADD, (id, partname)))
    
    def delete(self, id):
        self.storageComponent.delete(document)
        self._enqueue((DELETE, id))
    
    def refresh(self):
        for id in self.storageComponent:
            self.addId(id)
        self.optimize()
    
    def optimize(self):
        removeAllDuplicates
    
    def _tick(self):
        self._reactor.removeTimer(self._token)
        element = self._dequeue()
        if not element:
            return
        job, data = element
        if job == ADD:
            self._actualAdd(*data)
        else: #DELETE
            id = data
            self._actualDelete(data)
            
        self._reactor.addTimer(self._frequency, self._tick)
    
    def _actualAdd(self, id, partname):
        #try:
        document = self._storageComponent.getStream(id, partname).getvalue()
        #except: HierarchicalStorageError
            
        self._sink.add(id, partname, document)
    
    def _actualDelete(self, id):
        self._sink.delete(id)


    #two level tree to (somewhat) reduce the huge cost of copying the lists all the time
    def _enqueue(self, element):
        if not self._queues or (len(self._queues[0]) > QUEUE_NODES_LENGTH):
            self._queues.insert(0, [])
        self._queues[0].insert(0, element)
        
    def _dequeue(self):
        if not self._queues:
            return None
        lastQueue = self._queues[-1]
        if not lastQueue:
            self._queues = self._queues[:-1]
            if not self._queues:
                return None
            lastQueue = self._queues[-1]
        result = lastQueue[-1]
        self._queues[-1] = lastQueue[:-1]
        return result

#todo: file stuff: dwz transaction queue daarop gebaseerd

#todo: 'go into inactive state if nothing to do'
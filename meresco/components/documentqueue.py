from meresco.framework import Transparant
from storage.hierarchicalstorage import HierarchicalStorageError

INTERNAL_PARTNAME = 'queued'
UNKNOWN_PARTNAME = 'unknown'

QUEUE_NODES_LENGTH = 100

class DocumentQueue(Transparant):
    
    def __init__(self, storageComponent, reactor, frequency):
        reactor.addWriter(1, lambda *args: None) #workaround: 1 is sys.stdout
        
        Transparant.__init__(self)
        self._storageComponent = storageComponent
        self._reactor = reactor
        self._frequency = frequency
        self._queues = []
        self._token = self._reactor.addTimer(self._frequency, self._tick)
        
        self._instructions = {
            'ADD': self._actualAdd,
            'DELETE': self._actualDelete,
            'REFRESH': self._actualRefresh
        }
    
    def add(self, id, partname, document):
        if not type(document) == str:
            raise Exception("Document should be string")
        self._storageComponent.add(id, INTERNAL_PARTNAME, document)
        self._enqueueAndLog(('ADD', id))
    
    def delete(self, id):
        self._storageComponent.deletePart(id, INTERNAL_PARTNAME)
        self._enqueueAndLog(('DELETE', id))
    
    def refresh(self):
        self._enqueueAndLog(('REFRESH', 'id_is_ignored'))
    
    def optimize(self):
        removeAllDuplicates
    
    def _tick(self):
        try:
            element = self._dequeue()
            if not element:
                return
            instruction, id = element
            self._instructions[instruction](id)
        finally:
            self._token = self._reactor.addTimer(self._frequency, self._tick)
    
    def _actualAdd(self, id):
        try:
            document = self._storageComponent.getStream(id, INTERNAL_PARTNAME).read()
        except HierarchicalStorageError:
            return # an order to delete has followed already
        self.do.add(id, UNKNOWN_PARTNAME, document)
    
    def _actualDelete(self, id):
        self.do.delete(id)
        
    def _actualRefresh(self):
        #KVS: het is een zooitje met die storage interface - dus hier er maar omheen hakken.
        hierarchicalStorage = self._storageComponent._storage
        for id, partName in hierarchicalStorage:
            self._enqueue((self._actualAdd, id))

    def _readFromFile(self, filename):
        raise NotImplemented
        remove(log2name)
        f = open(filename)
        for line in f.readlines:
            line = line.strip()
            parts = tuple(line.split('\t'))
            self._enqueue(parts)
        f.close()
    
    def _writeLogLine(self, element):
        raise NotImplemented
        self._log.write('\t'.join(element) + '\n')
        self._log.flush()
        
    def _recreateLog(self):
        raise NotImplemented
        log2 = open('...')
        for element in self._queue.allElements():
            log2.write('\t'.join(element) + '\n')
        log2.close()
        move(log2Name, logName)
    
    def _enqueueAndLog(self, element):
        #self._writeLogLine(element)
        self._enqueue(element)

    def _enqueue(self, element):
        """This is implemented using a two level tree to reduce the cost of copying the lists all the time"""
        if not self._queues or (len(self._queues[0]) > QUEUE_NODES_LENGTH):
            self._queues.insert(0, [])
        self._queues[0].insert(0, element)
        
    def _dequeue(self):
        """This is implemented using a two level tree to reduce the cost of copying the lists all the time"""
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
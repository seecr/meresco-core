## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#
#    This file is part of Meresco Core.
#
#    Meresco Core is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Meresco Core is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Meresco Core; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
from meresco.framework import Transparant
from storage.hierarchicalstorage import HierarchicalStorageError

INTERNAL_PARTNAME = 'queued'
UNKNOWN_PARTNAME = 'unknown'

QUEUE_NODES_LENGTH = 100

ADDS_BEFORE_OPTIMIZE = 1000

class DocumentQueue(object):
    
    def __init__(self, storageComponent, index, reactor, frequency):
        self._storageComponent = storageComponent
        self._index = index
        self._reactor = reactor
        self._frequency = frequency
        self._queues = []
        self._token = self._reactor.addTimer(self._frequency, self._tick)
        self._optimizeCount = 0
        
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
    
    def _tick(self):
        if not self._index._writingAllowed:
            return
        try:
            element = self._dequeue()
            if not element:
                #probleemgebied, maar ik ben nog aan het schetsen hier....
                self._optimizeCount = 0
                self._index.optimize()
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
        self._index.add(id, UNKNOWN_PARTNAME, document)
        
        self._optimizeCount += 1
        if self._optimizeCount >= ADDS_BEFORE_OPTIMIZE:
            self._optimizeCount = 0
            self._index.optimize()
    
    def _actualDelete(self, id):
        self._index.delete(id)
        
    def _actualRefresh(self, ignoredId):
        #KVS: het is een zooitje met die storage interface - dus hier er maar omheen hakken.
        hierarchicalStorage = self._storageComponent._storage
        for id, partName in hierarchicalStorage:
            self._enqueue(("ADD", id))
        #self._removeAllDuplicates()

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
        
    def __len__(self):
        result = 0
        for queue in self._queues:
            result += len(queue)
        return result

#todo: file stuff: dwz transaction queue daarop gebaseerd

#todo: 'go into inactive state if nothing to do'

CHUNKSIZE = 1000

import os
from math import floor
from thread import allocate_lock
from shutil import move
from time import sleep

class UniqueNumberGenerator:

        def __init__(self, filename):
                self.filename = filename
                if os.path.exists(filename):
                        self._nr = self._read()
                else:
                        self._nr = -1
                self._reserved = self._nr
                self._lock = allocate_lock()

        def next(self):
                self._lock.acquire()
                try:
                        self._nr += 1
                        assert not sleep(0.000001) # yield current thread (forces tests to fail always if there would not be locking, as opposed to non-deterministic failures)
                        self._reserve(self._nr)
                        result = self._nr
                finally:
                        self._lock.release()
                return result

        def _reserve(self, nr):
                reserved =  int(floor(nr / (1.0 * CHUNKSIZE)) + 1) * CHUNKSIZE
                if reserved > self._reserved:
                        self._write(reserved)
                        self._reserved = reserved

        def _write(self, nr):
                f = open(self.filename + '.atomic', 'w')
                try:
                        f.write(str(nr))
                finally:
                        f.close()
                move(self.filename + '.atomic', self.filename)

        def _read(self):
                f = open(self.filename)
                try:
                        result = int(f.read())
                finally:
                        f.close()
                return result
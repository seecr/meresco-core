from __future__ import with_statement

class Configuration(object):
    def __init__(self, aDictionary):
        self._dictionary = aDictionary
    def configuration(self):
        return self._dictionary

def readConfig(filename):
    result = {}
    with open(filename) as f:
        for line in f:
            if line.strip() and line.strip()[0] != '#':
                k,v = line.strip().split('=', 1)
                result[k.strip()] = v.strip()
    return result
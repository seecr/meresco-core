
from unittest import TestCase

from meresco.components.contextset import ContextSet, ContextSetException, ContextSetList
from cStringIO import StringIO

class ContextSetTest(TestCase):
    def setUp(self):
        stream = StringIO("\n".join([
            "\t".join(["query.field1", "actualfield1"]),
            "\t".join(["field1", "actualfield1"]),
            "\t".join(["field2", "actualfield2"]),
            "\t".join(["field2", "actualotherfield2"])]))
        self.set = ContextSet('test', stream)
    
    def testLookup(self):
        self.assertEquals('test', self.set.name)
        self.assertEquals('actualfield1', self.set.lookup('test.query.field1'))
        self.assertEquals('actualfield1', self.set.lookup('test.field1'))
        self.assertEquals('actualfield2', self.set.lookup('test.field2'))
        self.assertEquals('nosuchfield', self.set.lookup('nosuchfield'))
        self.assertEquals('test.nosuchfield', self.set.lookup('test.nosuchfield'))
        self.assertEquals('otherset.field', self.set.lookup('otherset.field'))
        
    def testReverseLookup(self):
        self.assertEquals('test.query.field1', self.set.reverseLookup('actualfield1'))
        self.assertEquals('test.field2', self.set.reverseLookup('actualfield2'))
        self.assertEquals('test.field2', self.set.reverseLookup('actualotherfield2'))
        self.assertEquals('nosuchfield', self.set.reverseLookup('nosuchfield'))
        
    def testLookupInList(self):
        setlist = ContextSetList()
        setlist.add(ContextSet('set1', StringIO("field\tactualfield\nfield1\tactualfield1")))
        setlist.add(ContextSet('set2', StringIO("field\tactualfield\nfield2\tactualfield2")))
        self.assertEquals('actualfield', setlist.lookup('set1.field'))
        self.assertEquals('actualfield', setlist.lookup('set2.field'))
        self.assertEquals('actualfield2', setlist.lookup('set2.field2'))
        self.assertEquals('set2.field2', setlist.reverseLookup('actualfield2'))
        self.assertEquals('set1.field1', setlist.reverseLookup('actualfield1'))
        self.assertEquals('set1.field', setlist.reverseLookup('actualfield'))
        try:
            setlist.lookup('set1.field3')
            self.fail()
        except ContextSetException, e:
            self.assertEquals('Unknown field: set1.field3', str(e))
        self.assertEquals('noreversefield', setlist.reverseLookup('noreversefield'))
        try:
            setlist.lookup('unsupportedset.field3')
            self.fail()
        except ContextSetException, e:
            self.assertEquals('Unsupported contextset: unsupportedset', str(e))
        # Exception to the exception, can't help it.
        self.assertEquals('nosetfield', setlist.lookup('nosetfield'))
        
            
    #def testApplyReverseContextSets(self):
        

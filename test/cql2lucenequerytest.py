from unittest import TestCase
from cqlparser import parseString
from meresco.components.lucene import CQL2LuceneQuery

class DummyIndex(object):
    def executeQuery(*args, **kwargs):
        pass

class Cql2LuceneQueryTest(TestCase):
    def testLoggingCQL(self):
        convertor = CQL2LuceneQuery({})
        convertor.addObserver(DummyIndex())
        def logShunt(**dict):
            self.dict = dict
        convertor.log = logShunt
        convertor.executeCQL(parseString("term"))
        self.assertEquals({'clause': 'term'}, self.dict)
        convertor.executeCQL(parseString("field=term"))
        self.assertEquals({'clause': 'field = term'}, self.dict)
        convertor.executeCQL(parseString("field =/boost=1.1 term"))
        self.assertEquals({'clause': 'field =/boost=1.1 term'}, self.dict)
        convertor.executeCQL(parseString("field exact term"))
        self.assertEquals({'clause': 'field exact term'}, self.dict)
        convertor.executeCQL(parseString("term1 AND term2"))
        self.assertEquals({'clause': 'term1'}, self.dict)
        convertor.executeCQL(parseString("(term)"))
        self.assertEquals({'clause': 'term'}, self.dict)


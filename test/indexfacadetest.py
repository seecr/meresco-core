from PyLucene import MatchAllDocsQuery
from meresco.components.lucene import LuceneIndex2, Document2
from meresco.components.lucene import LuceneDocIdTrackerDecorator
from cq2utils import CQ2TestCase, CallTrace

from meresco.components.lucene import IndexFacade


class IndexFacadeTest(CQ2TestCase):

    def setUp(self):
        CQ2TestCase.setUp(self)
        self.index = LuceneIndex2(self.tempdir, CallTrace('timer'))
        tracker = LuceneDocIdTrackerDecorator(self.index)
        self.facade = IndexFacade(self.index)

    def testAddBatches(self):
        doc1 = Document2('id0')
        doc1.addIndexedField('field0', 'term0')
        self.facade.addDocument(doc1)
        self.assertEquals(0, len(self.facade.executeQuery(MatchAllDocsQuery())))
        self.assertEquals(0, len(self.index.executeQuery(MatchAllDocsQuery())))
        self.facade.flush()
        self.assertEquals(1, len(self.facade.executeQuery(MatchAllDocsQuery())))
        self.assertEquals(1, len(self.index.executeQuery(MatchAllDocsQuery())))

    def testDelete(self):
        doc0 = Document2('id0')
        doc0.addIndexedField('field0', 'term0')
        self.facade.addDocument(doc0)
        self.facade.flush()
        self.facade.delete('id0')
        self.assertEquals(1, len(self.facade.executeQuery(MatchAllDocsQuery())))
        self.facade.flush()
        self.assertEquals(0, len(self.facade.executeQuery(MatchAllDocsQuery())))

    def testDeleteIsSmart(self):
        self.index.delete = lambda anId: "should not reach here"+0
        doc0 = Document2('id0')
        doc0.addIndexedField('field0', 'term0')
        self.facade.addDocument(doc0)
        self.facade.delete('id0')
        self.assertEquals(0, len(self.facade.executeQuery(MatchAllDocsQuery())))
        self.facade.flush()
        self.assertEquals(0, len(self.facade.executeQuery(MatchAllDocsQuery())))

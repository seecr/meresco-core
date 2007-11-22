from meresco.framework import Observable
from meresco.components.dictionary import DocumentDict
from amara.bindery import is_element, root_base
from amara.binderytools import bind_string, create_document

class Accumulate(Observable):
    def __init__(self, rootTagName):
        Observable.__init__(self)
        self._rootTagName = rootTagName
        self._reset()

    def _reset(self):
        self._identifier = None
        doc = create_document()
        self._rootTag = doc.xml_create_element(unicode(self._rootTagName))

    def add(self, identifier, partName, dataNode):
        assert is_element(dataNode) and type(dataNode) != root_base, 'Expects amara elements, not amara documents.'

        if self._identifier and self._identifier != identifier:
            self.do.add(self._identifier, self._rootTagName, self._rootTag)
            self._reset()

        self._identifier = identifier
        self._rootTag.xml_append(dataNode)

    def finish(self):
        if self._identifier:
            self.do.add(self._identifier, self._rootTagName, self._rootTag)
            self._reset()

    def unknown(self, message, *args, **kwargs):
        return self.all.unknown(message, *args, ** kwargs)
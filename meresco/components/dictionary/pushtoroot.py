
from meresco.framework.observable import Observable
from meresco.components.dictionary import DocumentField

import re

class PushToRoot(Observable):

    def fieldsForField(self, documentField):
        for newFieldname in self._splitFieldname(documentField.key):
            yield DocumentField(newFieldname, documentField.value, **documentField.options)
    
    def _splitFieldname(self, fieldname):
        parts = fieldname.split(".")
        leftHandSide = ''
        for part in parts:
            yield leftHandSide + part
            leftHandSide += part + '.'

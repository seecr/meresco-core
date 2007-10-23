
from meresco.framework.observable import Observable
from meresco.components.dictionary import DocumentField

import re

class Transform(Observable):
    def __init__(self, sourceFieldname, targetFieldname, transformer):
        Observable.__init__(self)
        self.sourceFieldname = sourceFieldname
        self.targetFieldname = targetFieldname
        self.transformer = transformer

    def fieldsForField(self, documentField):
        if self.sourceFieldname == documentField.key:
            for part in self.transformer(documentField.value):
                yield DocumentField(self.targetFieldname, part)

class CleanSplit:
    def __init__(self, separator):
        self.separator = separator

    def __call__(self, s):
        return [part.strip() for part in s.split(self.separator)]

def years(s):
    yearRe = re.compile('\d{4}')
    return yearRe.findall(s)


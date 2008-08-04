
from meresco.framework import Observable

from re import compile
from StringIO import StringIO
from xml.sax.saxutils import escape as escapeXml

correctNameRe = compile(r'^\w+$')

class Fields2XmlTx(Observable):
    def __init__(self, transaction, partName):
        Observable.__init__(self)
        if not correctNameRe.match(partName):
            raise Fields2XmlException('Invalid name: "%s"' % partName)
        self._identifier = None
        self._fields = []
        self._partName = partName
        self._transaction = transaction
        
    def addField(self, name, value):
        if name == '__id__':
            self._identifier = value
            return
        self._fields.append((name,value))

    def finalize(self):
        xml = '<%s>%s</%s>' % (self._partName, generateXml(self._fields), self._partName)
        
        self._transaction.do.store(self._identifier, self._partName, xml)

def splitName(name):
    result = name.split('.')
    if len(result) == 1:
        return '//', name
    return '//' + '/'.join(result[:-1]), result[-1]

def createTag(tagName, value):
    return '<%s>%s</%s>' % (tagName, escapeXml(value), tagName)

def _generateXml(fields):
    currentPath = '//'
    for name, value in fields:
        for namePart in name.split('.'):
            if not correctNameRe.match(namePart):
                raise Fields2XmlException('Invalid name: "%s"' % name)
            
        parentPath, tagName = splitName(name)
        while parentPath != currentPath:
            if currentPath in parentPath:
                parentTagsToAdd = [tag for tag in parentPath[len(currentPath):].split('/') if tag]
                for tag in parentTagsToAdd:
                    yield('<%s>' % tag)
                currentPath = parentPath
            else:
                tag = currentPath.split('/')[-1]
                currentPath = '/'.join(currentPath.split('/')[:-1])
                yield('</%s>' % tag)
                
                
        yield createTag(tagName, value)
    if currentPath != '//':
        parentTagsToRemove = currentPath[len('//'):].split('/')
        for tag in reversed(parentTagsToRemove):
            yield('</%s>' % tag)
        

def generateXml(fields):
    return ''.join(_generateXml(fields))

class Fields2XmlException(Exception):
    pass
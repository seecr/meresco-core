

from meresco.framework.observable import Observable
from re import compile

lastnameExpr = r'^(?P<lastname>[A-Za-z]+)'

def removeDots(initials):
    return [initial for initial in initials.lower().replace('.','') if initial]

def lower(initials):
    return [initial for initial in initials.lower() if initial]

def getInitials(firstNames):
    return [firstName[0].lower() for firstName in firstNames.split(' ')]

expressions = [
    (lastnameExpr + r', (?P<initials>(?:[A-Za-z]\.)+)\s*(?:|\([a-zA-Z\s]+\))$', removeDots),#A.B.C.  (WhaAAtevaesdf)
    (lastnameExpr + r', (?P<initials>[A-Z]+)$', lower), #ABC
    (lastnameExpr + r', (?P<initials>[A-Za-z ]+)$', getInitials), #Aaaa Bbbb Cccc
]

compiledExpressions = [(compile(expression),f) for expression,f in expressions]

def breakUp(name):
    for expression, initialsPostProcess in compiledExpressions:
        m = expression.match(name)
        if m:
            lastname = m.groupdict()['lastname'].lower()
            print name, '-->', m.groups()
            initials = initialsPostProcess(m.groupdict()['initials'])
            #initials = [initial for initial in initials] # voor thijs
            return lastname, "", initials[0], initials
    return None

class NameNormalize(Observable):
    pass


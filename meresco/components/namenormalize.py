

from meresco.framework.observable import Observable
from re import compile

lastnameExpr = r'^(?P<lastname>[A-Za-z]+)'

def removeDots(initials):
    return initials.lower().replace('.','')

def lower(initials):
    return initials.lower()

def getInitials(firstNames):
    return "".join([_firstChar(firstName).lower() for firstName in firstNames.split(' ')])

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
            #print name, '-->', m.groups()
            initials = initialsPostProcess(m.groupdict()['initials'])
            return lastname, initials, ""
    return None
    
    
def dots(s):
    return "".join([c + "." for c in s])

def _firstChar(s):
    return s and s[0]

def helsing(aTuple):
    return aTuple[0].capitalize()
    
def helsing_a_v(aTuple):
    prefix = dots(getInitials(aTuple[2]))
    l = [aTuple[0].capitalize(), dots(_firstChar(aTuple[1])).upper()]
    if prefix:
        l.append(prefix)
    return ", ". join(l)
    
def helsing_ab_van(aTuple):
    prefix = aTuple[2]
    l = [aTuple[0].capitalize(), dots(aTuple[1]).upper()]
    if prefix:
        l.append(prefix)
    return ", ". join(l)

class NameNormalize(Observable):
    pass


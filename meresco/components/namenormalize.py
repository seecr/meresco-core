

from meresco.framework.observable import Observable
from re import compile

lastnameExpr = r'^(?P<lastname>[A-Za-z]+)'

def removeDots(initials):
    return initials.lower().replace('.','')

def lower(initials):
    return initials.lower()

def getInitials(firstNames):
    return "".join([firstName[0].lower() for firstName in firstNames.split(' ')])

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
    
def _firstChar(s):
    return s and s[0]

def helsing(aTuple):
    return aTuple[0]
    
def helsing_a_v(aTuple):
    return "%s,%s,%s" % (aTuple[0], _firstChar(aTuple[1]), getInitials(aTuple[2]))
    
def helsing_ab_van(aTuple):
    return ",".join(aTuple).replace(" ", "")

class NameNormalize(Observable):
    pass


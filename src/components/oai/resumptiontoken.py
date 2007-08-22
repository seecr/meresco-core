

def resumptionTokenFromString(s):
    try:
        result = ResumptionToken()
        result.loadString(s)
        return result
    except ResumptionTokenException, e:
        return None

class ResumptionTokenException(Exception):
    pass

class ResumptionToken:

    SHORT = {
        'm': '_metadataPrefix',
        'c': '_continueAt',
        'f': '_from',
        'u': '_until',
        's': '_set'}

    def __init__(self,
        _metadataPrefix = '',
        _continueAt = '0',
        _from = '',
        _until = '',
        _set = ''):
        self._metadataPrefix = _metadataPrefix
        self._continueAt = _continueAt
        self._from = _from or '' #blank out "None"
        self._until = _until or ''
        self._set = _set or ''

    def __str__(self):
        short = ResumptionToken.SHORT
        return '|'.join(map(lambda k: "%s%s" %(k, self.__dict__[short[k]]), short.keys()))

    def __repr__(self):
        return repr(str(self))

    def __eq__(self, other):
        return \
            ResumptionToken == other.__class__ and \
            self._metadataPrefix == other._metadataPrefix and \
            self._continueAt == other._continueAt and \
            self._from == other._from and \
            self._until == other._until and \
            self._set == other._set

    def loadString(self, s):
        resumptDict = dict(((part[0], part[1:]) for part in s.split('|') if part))
        if set(ResumptionToken.SHORT.keys()) != set(resumptDict.keys()):
            raise ResumptionTokenException()
        for k,v in resumptDict.items():
            setattr(self, ResumptionToken.SHORT[k], v)

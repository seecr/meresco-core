class Resource(object):
    def __init__(self, subject):
        self._subject = subject

    def __del__(self):
        self._subject.close()

    def __getattr__(self, name):
        return getattr(self._subject, name)

    def close(self):
        raise Exception('hell')
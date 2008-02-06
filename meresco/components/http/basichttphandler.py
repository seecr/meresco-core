from utils import notFoundHtml

from meresco.framework import Observable

class BasicHttpHandler(Observable):

    def handleRequest(self, *args, **kwargs):
        yielded = False
        stuff = self.all.handleRequest(*args, **kwargs)
        for x in stuff:
            yielded = True
            yield x
        if not yielded:
            yield notFoundHtml
            yield "<html><body>404 Not Found</body></html>"

    def unknown(self, method, *args, **kwargs):
        return self.all.unknown(method, *args, **kwargs)
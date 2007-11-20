from os.path import isfile, join

from meresco.components.http import utils as httputils

import magic
magicCookie = magic.open(magic.MAGIC_MIME)
magicCookie.load()

import mimetypes
mimetypes.init()

class FileServer:
    def __init__(self, documentRoot):
        self._documentRoot = documentRoot

    def handleRequest(self, port=None, Client=None, RequestURI=None, Method=None, Headers=None, **kwargs):

        if not self.fileExists(RequestURI):
            yield httputils.notFoundHtml
            for line in ['<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">',
"<html><head>",
"<title>404 Not Found</title>",
"</head><body>",
"<h1>Not Found</h1>",
"<p>The requested URL %s was not found on this server.</p>" % RequestURI,
"<hr>",
"<address>Weightless Server at localhost Port 8080</address>",
"</body></html>"]:
                yield line
            raise StopIteration

        yield 'HTTP/1.0 200 Ok\r\n'
        filename = self._filenameFor(RequestURI)
        ext = filename.split(".")[-1]
        try:
            extension = mimetypes.types_map["."+ext]
        except KeyError:
            extension = "text/plain"
        yield "Content-Type: %s\r\n" % extension
        yield "\r\n"

        fp = open(filename)
        for line in fp:
            yield line
        fp.close()


    def _filenameFor(self, filename):
        while filename and filename[0] == '/':
            filename = filename[1:]
        return join(self._documentRoot, filename)

    def fileExists(self, filename):
        return isfile(self._filenameFor(filename))

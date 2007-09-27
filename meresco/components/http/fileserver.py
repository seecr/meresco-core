from os.path import isfile, join

import magic
magicCookie = magic.open(magic.MAGIC_MIME)
magicCookie.load()

class FileServer:
    def __init__(self, documentRoot):
        self._documentRoot = documentRoot

    def handleRequest(self, aRequest):
        if not self.fileExists(aRequest.path):
            aRequest.setResponseCode(404)
            aRequest.setHeader("Content-Type", "text/html")
            aRequest.write("""<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>404 Not Found</title>
</head><body>
<h1>Not Found</h1>
<p>The requested URL %s was not found on this server.</p>
<hr>
<address>Weightless Server at localhost Port 8080</address>
</body></html>""" % aRequest.path)
            return

        fp = open(self._filenameFor(aRequest.path))
        line = fp.readline()
        magicResult = magicCookie.buffer(line)
        aRequest.setHeader("Content-Type", magicResult)
        try:
            aRequest.write(line)
            for line in fp:
                aRequest.write(line)
        finally:
            fp.close()


    def _filenameFor(self, filename):
        while filename[0] == '/':
            filename = filename[1:]
        return join(self._documentRoot, filename)

    def fileExists(self, filename):
        return isfile(self._filenameFor(filename))

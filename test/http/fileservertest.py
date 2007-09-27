from unittest import TestCase

from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

from meresco.components.http.observablehttpserver import WebRequest
from meresco.components.http.fileserver import FileServer

class FileServerTest(TestCase):

    def setUp(self):
        self.directory = mkdtemp()

    def tearDown(self):
        rmtree(self.directory)

    def testServeNoneExistingFile(self):
        request = WebRequest(port=80, Client=('localhost', 9000), RequestURI="/doesNotExist", Method="GET", Headers={})

        fileServer = FileServer(self.directory)
        fileServer.handleRequest(request)

        self.assertEquals(404, request.responseCode)
        self.assertTrue("404 Not Found" in ''.join(request.generateResponse()))

    def testFileExists(self):
        server = FileServer(self.directory)
        self.assertFalse(server.fileExists("/filename"))
        self.assertFalse(server.fileExists("/"))

        open(join(self.directory, 'filename'), "w").close()
        self.assertTrue(server.fileExists("/filename"))

        self.assertFalse(server.fileExists("//etc/shadow"))

    def testServeFile(self):

        request = WebRequest(port=80, Client=('localhost', 9000), RequestURI="/someFile", Method="GET", Headers={})

        f = open(join(self.directory, 'someFile'), 'w')
        f.write("Some Contents")
        f.close()

        fileServer = FileServer(self.directory)
        fileServer.handleRequest(request)

        self.assertEquals(200, request.responseCode)
        self.assertTrue("Some Contents" in ''.join(request.generateResponse()))

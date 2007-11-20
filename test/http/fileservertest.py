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
        fileServer = FileServer(self.directory)
        response = ''.join(fileServer.handleRequest(port=80, Client=('localhost', 9000), RequestURI="/doesNotExist", Method="GET", Headers={}))

        self.assertTrue("HTTP/1.0 404 Not Found" in response, response)
        self.assertTrue("<title>404 Not Found</title>" in response)

    def testFileExists(self):
        server = FileServer(self.directory)
        self.assertFalse(server.fileExists("/filename"))
        self.assertFalse(server.fileExists("/"))

        open(join(self.directory, 'filename'), "w").close()
        self.assertTrue(server.fileExists("/filename"))

        self.assertFalse(server.fileExists("//etc/shadow"))

    def testServeFile(self):
        f = open(join(self.directory, 'someFile'), 'w')
        f.write("Some Contents")
        f.close()

        fileServer = FileServer(self.directory)
        response = ''.join(fileServer.handleRequest(port=80, Client=('localhost', 9000), RequestURI="/someFile", Method="GET", Headers={}))

        self.assertTrue("HTTP/1.0 200 Ok" in response)
        self.assertTrue("Some Contents" in response)

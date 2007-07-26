from urllib import urlopen
from threading import Thread

class GetURL:
    """Untested: "can't possibly break" and testing is 10x more work than the actual code"""
    
    def __init__(self, url):
        self._url = url

    def unknown(self, methodName, *args):
        method = lambda: urlopen(self._url).read()
        thread = Thread(target=method)
        #The program exits when only Daemon threads are left.
        thread.setDaemon(True)
        thread.start()

from meresco.framework import Observable

class OaiMain(Observable):

    def handleRequest(self, webrequest):
        verb = webrequest.args.get('verb',[None])[0]
        message = verb and verb[0].lower() + verb[1:] or ''
        return self.any.unknown(message, webrequest)
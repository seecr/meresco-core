
from merescocore.framework import Observable

class ArgumentsInSession(Observable):

    def handleRequest(self, session, arguments = {}, *args, **kwargs):
        for k,v in arguments.items():
            if not k in session:
                session[k] = []
            for arg in v:
                if arg[0] in '+-':
                    sign, source = arg[0], arg[1:]
                else:
                    sign = '+'
                    source = repr(arg)
                try:
                    value = eval(source, {'__builtins__': {}})
                except Exception, e:
                    yield 'HTTP/1.0 400 Bad Request\r\n\r\n' + str(e)
                    return
                if sign == '+':
                    if not value in session[k]:
                        session[k].append(value)
                elif sign == '-' and value in session[k]:
                        session[k].remove(value)
        yield self.all.handleRequest(session=session, *args, **kwargs)
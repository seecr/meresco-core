class TimerForTestSupport(object):
    def addTimer(self, time, callback):
        callback()
        return (time,callback)
    def removeTimer(self, token):
        pass


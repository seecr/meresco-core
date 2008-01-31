from time import sleep

class TimerForTestSupport(object):
    def addTimer(self, time, callback):
        callback()

        sleep(0.01)
        return (time,callback)
    def removeTimer(self, token):
        pass


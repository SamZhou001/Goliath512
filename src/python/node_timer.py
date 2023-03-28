from rpyc import Service
from rpyc import connect
import threading
import constants


class Timer(Service):
    def __init__(self, port, isBnode):
        self.isBnode = isBnode
        self.port = port
        threading.Timer(constants.PING_TIMER, self.ping).start()

    def ping(self):
        conn = connect('localhost', self.port)
        if self.isBnode:
            conn.root.check_heartbeat()
            threading.Timer(2 * constants.PING_TIMER, self.ping).start()
        else:
            conn.root.ping()
            threading.Timer(constants.PING_TIMER, self.ping).start()
        conn.close()

if __name__ == "__main__":
    pass

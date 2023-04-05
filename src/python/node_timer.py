from rpyc import Service
from rpyc import connect
import threading
import constants

class PingTimer(Service):
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

class DownloadTimer(Service):
    def __init__(self, port, cid):
        self.port = port
        self.cid = cid
        threading.Timer(constants.DOWNLOAD_TIMER, self.ping).start()

    def ping(self):
        conn = connect('localhost', self.port)
        conn.root.download_over(self.cid)
        conn.close()

if __name__ == "__main__":
    pass

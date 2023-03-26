from rpyc import Service
from rpyc import connect
import threading
import constants


class BNode_Timer(Service):
    def __init__(self, bnode_port):
        print("Timer initialized")
        self.bnode_port = bnode_port
        self.ping()

    def ping(self):
        conn = connect('localhost', self.bnode_port)
        conn.root.check_heartbeat()
        conn.close()
        threading.Timer(constants.PING_TIMER, self.ping).start()


if __name__ == "__main__":
    pass

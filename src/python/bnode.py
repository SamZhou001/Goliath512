from rpyc import Service
from rpyc.utils.server import ThreadedServer
from rpyc import connect
import time, threading

import constants

class BootstrapNode(Service):
    def __init__(self, port):
        print("Bootstrap node initialized")
        self.port = port
        self.peer_store = {}
        self.last_pinged = {}
        self.check_heartbeat()

    def exposed_ping(self, peer_id, port):
        #print("Received ping from " + str(peer_id))
        if peer_id not in self.peer_store:
            conn = connect('localhost', port)
            conn.root.send_peers(self.peer_store)
        self.peer_store[peer_id] = port
        self.last_pinged[peer_id] = port

    def check_heartbeat(self):
        self.peer_store = self.last_pinged
        self.last_pinged = {}
        threading.Timer(constants.PING_TIMER, self.check_heartbeat).start()

if __name__ == "__main__":
    node = BootstrapNode(18861)
    t = ThreadedServer(node, port=node.port)
    t.start()
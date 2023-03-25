from rpyc import Service
from rpyc import connect
import threading

import constants

# OUTSTANDING BUG: check_heartbeat does not see updated peer_store

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
            conn.close()
        self.last_pinged[peer_id] = port

    def check_heartbeat(self):
        print(self.peer_store)
        for peer_id in self.peer_store:
            if peer_id not in self.last_pinged:
                self.process_dead_node(peer_id)
        self.last_pinged = {}
        threading.Timer(constants.PING_TIMER, self.check_heartbeat).start()

    def process_dead_node(self, dead_node):
        del self.peer_store[dead_node]
        for peer_id in self.last_pinged:
            conn = connect('localhost', self.last_pinged[peer_id])
            conn.root.remove_peer(dead_node)
            conn.close()

if __name__ == "__main__":
    pass
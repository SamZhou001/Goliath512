from rpyc import Service
from rpyc import connect
from threading import Thread
import time
import constants
from bnode_timer import BNode_Timer

# OUTSTANDING BUG: check_heartbeat does not see updated peer_store


class BootstrapNode(Service):
    def __init__(self, port):
        print("Bootstrap node initialized")
        self.port = port
        self.peer_store = {}
        self.last_pinged = {}
        self.timer_init = False
        self.bnode_timer = None

    def exposed_ping(self, peer_id, port):
        if not self.timer_init:
            self.bnode_timer = BNode_Timer(self.port)
            self.timer_init = True
        print("Received ping from " + str(peer_id))
        if peer_id not in self.peer_store:
            conn = connect('localhost', port)
            conn.root.send_peers(self.peer_store)
            self.peer_store[peer_id] = port
            conn.close()
        self.last_pinged[peer_id] = port
        print(self.peer_store)

    def exposed_check_heartbeat(self):
        print("RECEIVED HEARTBEAT")
        for peer_id in self.peer_store:
            if peer_id not in self.last_pinged:
                self.process_dead_node(peer_id)
        self.peer_store = self.last_pinged
        self.last_pinged = {}
        print(self.peer_store)

    def process_dead_node(self, dead_node):
        for peer_id in self.last_pinged:
            conn = connect('localhost', self.last_pinged[peer_id])
            conn.root.remove_peer(dead_node)
            conn.close()


if __name__ == "__main__":
    pass

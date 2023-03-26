from rpyc import Service
from rpyc import connect
from threading import Thread
import copy
from node_timer import Timer

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
            self.bnode_timer = Timer(self.port, True)
            self.timer_init = True
        #print("Received ping from " + str(peer_id))
        if peer_id not in self.peer_store:
            conn = connect('localhost', port)
            conn.root.send_peers(self.peer_store)
            self.peer_store[peer_id] = port
            conn.close()
        self.last_pinged[peer_id] = port

    def exposed_check_heartbeat(self):
        for peer_id in self.peer_store:
            if peer_id not in self.last_pinged:
                self.process_dead_node(peer_id)
        self.peer_store = self.last_pinged
        self.last_pinged = {}

    def process_dead_node(self, dead_node):
        print(f"DEAD {dead_node}")
        last_pinged = copy.deepcopy(self.last_pinged)
        for peer_id in last_pinged:
            conn = connect('localhost', last_pinged[peer_id])
            conn.root.remove_peer(dead_node)
            conn.close()

if __name__ == "__main__":
    pass

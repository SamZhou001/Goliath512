from rpyc import Service
from rpyc import connect
from threading import Thread
import copy
from node_timer import PingTimer
import time

import constants

class BootstrapNode(Service):
    def __init__(self, port):
        #print("Bootstrap node initialized")
        self.port = port
        self.peer_store = {}
        self.last_pinged = {}
        self.region = "USA"
        self.timer_init = False
        self.bnode_timer = None

    def calculate_delay(self, region):
        region_1 = constants.REGIONS.index(self.region)
        region_2 = constants.REGIONS.index(region)
        return (constants.BASE_LATENCY + constants.DISTANCES[region_1][region_2] * constants.DELAY_RATE)/1000

    def exposed_ping(self, region, peer_id, port):
        time.sleep(self.calculate_delay(region))
        if not self.timer_init:
            self.bnode_timer = PingTimer(self.port, True)
            self.timer_init = True
        # print("Received ping from " + str(peer_id))
        if peer_id not in self.peer_store:
            self.peer_store[peer_id] = port
            conn = connect('localhost', port)
            conn.root.send_peers(self.region, self.peer_store)
            conn.close()
        self.last_pinged[peer_id] = port

    def exposed_check_heartbeat(self):
        peer_store = copy.deepcopy(self.peer_store)
        last_pinged = copy.deepcopy(self.last_pinged)
        for peer_id in peer_store:
            if peer_id not in last_pinged:
                self.process_dead_node(peer_id)
        self.peer_store = last_pinged
        self.last_pinged = {}

    def process_dead_node(self, dead_node):
        last_pinged = copy.deepcopy(self.last_pinged)
        for peer_id in last_pinged:
            conn = connect('localhost', last_pinged[peer_id])
            conn.root.remove_peer(self.region, dead_node)
            conn.close()

if __name__ == "__main__":
    pass

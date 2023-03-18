from rpyc.utils.server import ThreadedServer
import multiprocessing
import time

from node import Node
from bnode import BootstrapNode
import constants

class Network():
    def __init__(self, bnodePort):
        self.bnodePort = bnodePort
        self.bnode = BootstrapNode(bnodePort)
        self.nodes = {} #Map from peer_id of each node to the node itself; makes it easier to call individual node functions
        worker = multiprocessing.Process(target=self.add_job, args=(self.bnode,))
        worker.start()
    
    def add_node(self, config):
        config['bootstrap_port'] = constants.BOOTSTRAP_PORT
        node = Node(config)
        self.nodes[node.peer_id] = node
        worker = multiprocessing.Process(target=self.add_job, args=(node,))
        worker.start()

    def add_job(self, node):
        t = ThreadedServer(node, port=node.port)
        t.start()

if __name__ == "__main__":
    network = Network(constants.BOOTSTRAP_PORT)
    for config in constants.NODE_CONFIG:
        time.sleep(constants.SIM_INTERVAL)
        network.add_node(config)
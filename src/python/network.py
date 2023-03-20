from rpyc.utils.server import ThreadedServer
import multiprocessing
import time
import asyncio
from david.network import Server
import shutil
import os

from node import Node
from bnode import BootstrapNode
import constants


class Network():
    def __init__(self, bnodePort):
        self.bnodePort = bnodePort
        self.bnode = BootstrapNode(bnodePort)
        self.nodes = {}  # Map from peer_id of each node to the node itself; makes it easier to call individual node functions
        if os.path.exists('./storage'):
            shutil.rmtree('./storage')
        os.makedirs('./storage')
        worker = multiprocessing.Process(
            target=self.add_job, args=(self.bnode,))
        worker.start()

    def add_node(self, config):
        config['bootstrap_port'] = constants.BOOTSTRAP_PORT
        node = Node(config)
        self.nodes[node.peer_id] = node
        node_worker = multiprocessing.Process(
            target=self.add_job, args=(node,))
        node_worker.start()
        dht_worker = multiprocessing.Process(
            target=self.start_dht_server, args=(config['dht_port'],))
        dht_worker.start()

    def start_dht_server(self, port):
        server = Server()
        loop = asyncio.new_event_loop()
        loop.set_debug(True)

        loop.run_until_complete(server.listen(port))

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.stop()
            loop.close()

    def add_job(self, node):
        t = ThreadedServer(node, port=node.port)
        t.start()


async def test(network):
    network.nodes[100].generate_file("hi", 40)
    time.sleep(1)
    await network.nodes[100].upload("hi")

if __name__ == "__main__":
    network = Network(constants.BOOTSTRAP_PORT)
    for config in constants.NODE_CONFIG:
        time.sleep(constants.SIM_INTERVAL)
        network.add_node(config)
    asyncio.run(test(network))

from rpyc.utils.server import ThreadedServer
import multiprocessing
import time
import asyncio
from david.network import Server
import shutil
import os
from rpyc import connect

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

    def upload(self, peerId, fname, charCount):
        node = self.nodes[peerId]
        node.generate_file(fname, charCount)
        fpath = os.path.join(node.storage_path, "local",
                             node.modify_fname(fname))
        if not os.path.exists(fpath):
            raise Exception("No file found")
        cid = node.hash_file(fpath)
        port = node.port
        conn = connect('localhost', port)
        conn.root.upload(fname)
        conn.close()
        return cid

    def download(self, peerId, cid):
        port = self.nodes[peerId].port
        conn = connect('localhost', port)
        conn.root.download(cid)
        conn.close()

    def kill_node(self, peerId):
        conn = connect('localhost', self.nodes[peerId].port)
        conn.root.kill()
        conn.close()

    def revive_node(self, peerId):
        conn = connect('localhost', self.nodes[peerId].port)
        conn.root.revive()
        conn.close()


async def test(network):
    cid = network.upload(100, "hi", 40)
    time.sleep(1)
    network.download(101, cid)
    time.sleep(1)
    network.kill_node(100)
    network.kill_node(101)
    network.kill_node(102)
    time.sleep(2)
    network.revive_node(100)
    network.revive_node(101)

if __name__ == "__main__":
    network = Network(constants.BOOTSTRAP_PORT)
    for config in constants.NODE_CONFIG:
        time.sleep(constants.SIM_INTERVAL)
        network.add_node(config)
        # print(f"Add node {config['peer_id']}")
    time.sleep(constants.SIM_INTERVAL)
    asyncio.run(test(network))

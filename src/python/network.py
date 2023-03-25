from rpyc.utils.server import ThreadedServer
import multiprocessing
import time
import asyncio
from david.network import Server
import shutil
import os
import rpyc
from rpyc import connect

from node import Node
from bnode import BootstrapNode
import constants


class Network():
    def __init__(self, bnodePort):
        self.bnodePort = bnodePort
        self.bnode = BootstrapNode(bnodePort)
        self.nodes = {}  # Map from peer_id of each node to the node itself; makes it easier to call individual node functions
        self.workers = {}
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
        self.workers[node.peer_id] = (node_worker, dht_worker)

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

def upload(peerId, fname, charCount):
    node = network.nodes[peerId]
    node.generate_file(fname, charCount)
    fpath = os.path.join(node.storage_path, "local", node.modify_fname(fname))
    if not os.path.exists(fpath):
        raise Exception("No file found")
    cid = node.hash_file(fpath)
    port = node.port
    conn = connect('localhost', port)
    conn.root.upload(fname)
    conn.close()
    return cid

def download(peerId, cid):
    port = network.nodes[peerId].port
    conn = connect('localhost', port)
    conn.root.download(cid)
    conn.close()

async def test(network):
    cid = upload(100, "hi", 40)
    time.sleep(1)
    download(100, cid)
    time.sleep(1)
    #network.workers[100][0].terminate()

if __name__ == "__main__":
    network = Network(constants.BOOTSTRAP_PORT)
    for config in constants.NODE_CONFIG:
        time.sleep(constants.SIM_INTERVAL)
        network.add_node(config)
        print(f"Add node {config['peer_id']}")
    #asyncio.run(test(network))

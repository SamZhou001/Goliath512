from rpyc.utils.server import ThreadedServer
import multiprocessing
import time
import asyncio
from david.network import Server
import shutil
import os
from rpyc import connect
from david.utils import digest

from node import Node
from bnode import BootstrapNode
import constants

"""
import logging
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('david')
log.addHandler(handler)
log.setLevel(logging.DEBUG)
"""


class Network():
    def __init__(self, bnodePort):
        self.bnodePort = bnodePort
        self.bnode = BootstrapNode(bnodePort)
        self.nodes = {}  # Map from peer_id of each node to the node itself; makes it easier to call individual node functions
        if os.path.exists('./storage'):
            shutil.rmtree('./storage')
        os.makedirs('./storage')
        bootstrap_dht_worker = multiprocessing.Process(
            target=self.create_bootstrap_dht, args=())
        bootstrap_dht_worker.start()
        bootstrap_node_worker = multiprocessing.Process(
            target=self.add_job, args=(self.bnode,))
        bootstrap_node_worker.start()

    def create_bootstrap_dht(self):
        server = Server(node_id=digest(str(constants.BOOTSTRAP_DHT)))
        loop = asyncio.new_event_loop()
        loop.set_debug(True)

        loop.run_until_complete(server.listen(constants.BOOTSTRAP_DHT))

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.stop()
            loop.close()

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
        server = Server(node_id=digest(port))
        loop = asyncio.new_event_loop()
        loop.set_debug(True)
        loop.run_until_complete(server.listen(port))

        bootstrap_node = ('0.0.0.0', constants.BOOTSTRAP_DHT)
        loop.run_until_complete(server.bootstrap([bootstrap_node]))

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

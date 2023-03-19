from rpyc import Service
from rpyc.utils.server import ThreadedServer
from rpyc import connect
import threading
import random

import constants


class Node(Service):
    def __init__(self, config):
        self.peer_id = config['peer_id']
        self.port = config['port']
        self.bootstrap_port = config['bootstrap_port']
        self.storage_path = "./" + str(self.peer_id)
        self.connect_prob = config['connect_prob']
        self.dht = None  # Change later
        self.peers = {}  # mapping peerId -> port of connected peers
        threading.Timer(constants.PING_TIMER, self.ping).start()

    def add_peer(self, peer_id, port):
        print(f'Peer {self.peer_id} adds peer {peer_id}')
        self.peers[peer_id] = port

    # remove dead peers
    def exposed_remove_peer(self, peer_id):
        del self.peers[peer_id]

    def ping(self):
        conn = connect('localhost', self.bootstrap_port)
        conn.root.ping(self.peer_id, self.port)
        threading.Timer(constants.PING_TIMER, self.ping).start()

    def exposed_send_peers(self, peer_store):
        for peer_id in list(peer_store):
            port = peer_store[peer_id]
            conn = connect('localhost', port)
            conn.root.conn_request(self.peer_id, self.port, self.connect_prob)

    def exposed_conn_request(self, peer_id, port, connect_prob):
        if random.random() < min(connect_prob, self.connect_prob):
            self.add_peer(peer_id, port)
            conn = connect('localhost', port)
            conn.root.conn_ack(self.peer_id, self.port)

    def exposed_conn_ack(self, peer_id, port):
        self.add_peer(peer_id, port)


if __name__ == "__main__":
    config = {
        "peer_id": 50,
        "port": 7000,
        "bootstrap_port": 18861,
        "connect_prob": 1
    }
    node = Node(config)
    t = ThreadedServer(node, port=node.port)
    t.start()

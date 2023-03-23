from rpyc import Service
from rpyc import connect
from rpyc.utils.classic import download
import threading
import random
import string
import os
import hashlib
import shutil
from david.network import Server

import constants


class Node(Service):
    def __init__(self, config):
        self.peer_id = config['peer_id']
        self.port = config['port']
        self.bootstrap_port = config['bootstrap_port']
        self.storage_path = os.path.join("./storage", str(self.peer_id))
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
            os.makedirs(os.path.join(self.storage_path, "local"))
            os.makedirs(os.path.join(self.storage_path, "uploaded"))
        self.connect_prob = config['connect_prob']
        self.dht = None  # Change later
        self.peers = {}  # mapping peerId -> port of connected peers
        self.dht_port = config['dht_port']
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

    # Methods for connecting to peers
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

    def exposed_remove_peer():
        pass

    def exposed_has_file(self, cid, peer_id, port):
        upload_path = os.path.join(self.storage_path, 'uploaded')
        file_list = os.listdir(upload_path)
        for fname in file_list:
            fpath = os.path.join(upload_path, fname)
            fcid = self.hash_file(fpath)
            if fcid == cid:
                conn = connect('localhost', port)
                remote_path = os.path.join(
                    "./storage", str(peer_id), "local", fname)
                download(conn, remote_path, fpath)
                return True
        return False

    # Methods for DHT operations

    async def get(self, key):
        server = Server()
        await server.listen(0)
        bootstrap_node = ("127.0.0.1", self.dht_port)
        await server.bootstrap([bootstrap_node])
        result = await server.get(key)
        print("Get result:", result)
        server.stop()
        return result

    async def set(self, key, val):
        server = Server()
        await server.listen(0)
        bootstrap_node = ("127.0.0.1", self.dht_port)
        await server.bootstrap([bootstrap_node])
        await server.set(key, val)
        print(f"Set key-value pair {key}: {val}")
        server.stop()

    # Methods for upload
    def modify_fname(self, fname):
        return str(self.peer_id) + "_" + fname + ".txt"

    def generate_file(self, fname, strlen):
        with open(os.path.join(self.storage_path, "local", self.modify_fname(fname)), 'w') as f:
            randstr = ''.join(random.choice(
                string.ascii_letters + string.digits) for _ in range(strlen))
            f.write(randstr)

    def hash_file(self, fpath):
        content = ""
        with open(fpath, 'r') as f:
            content = f.read()
        return int(hashlib.sha256(content.encode('utf-8')).hexdigest(), 16) % 10**constants.HASH_DIGITS

    async def download(self, cid):
        for peer, port in self.peers.items():
            conn = connect('localhost', port)
            if (conn.root.has_file(cid, self.peer_id, self.port)):
                print("File downloaded. CID: " + cid)
                return
        # assume get result will be [(node_id, ip, port)]
        result = self.get(cid)
        for peer in result:
            ip = peer[1]
            port = peer[2]
            conn = connect(ip, port)
            if (conn.root.has_file(cid, self.peer_id, self.port)):
                print("File downloaded. CID: " + cid)
                return
        print("Failed to download file")

    async def upload(self, fname):
        fpath = os.path.join(self.storage_path, "local",
                             self.modify_fname(fname))
        if not os.path.exists(fpath):
            raise Exception("No file found")
        cid = self.hash_file(fpath)
        await self.set(cid, self.peer_id)
        await self.set(self.peer_id, self.port)
        old_path = os.path.join(
            self.storage_path, "local", self.modify_fname(fname))
        new_path = os.path.join(
            self.storage_path, "uploaded", self.modify_fname(fname))
        shutil.move(old_path, new_path)


if __name__ == "__main__":
    pass

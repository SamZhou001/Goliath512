import asyncio
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
from node_timer import Timer

import constants

class Node(Service):
    def __init__(self, config):
        self.alive = True
        self.peer_id = config['peer_id']
        self.port = config['port']
        self.bootstrap_port = config['bootstrap_port']
        self.storage_path = os.path.join("./storage", str(self.peer_id))
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
            os.makedirs(os.path.join(self.storage_path, "local"))
            os.makedirs(os.path.join(self.storage_path, "uploaded"))
        self.connect_prob = config['connect_prob']
        self.peers = {}  # mapping peerId -> port of connected peers
        self.dht_port = config['dht_port']
        self.timer = None
        self.timer_init = False
        self.init_timer()

    def execute_if_alive(func):
        def wrapper(self, *args, **kwargs):
            if self.alive:
                func(self, *args, **kwargs)
        return wrapper
    
    # Methods for pinging and adding peers
    def init_timer(self):
        if not self.timer:
            self.timer = Timer(self.port, False)
            self.timer_init = True
    
    @execute_if_alive
    def exposed_ping(self):
        conn = connect('localhost', self.bootstrap_port)
        conn.root.ping(self.peer_id, self.port)
        conn.close()

    def add_peer(self, peer_id, port):
        print(f'Peer {self.peer_id} adds peer {peer_id}')
        self.peers[peer_id] = port

    # remove dead peers
    @execute_if_alive
    def exposed_remove_peer(self, peer_id):
        if peer_id in self.peers:
            del self.peers[peer_id]

    # Methods for connecting to peers
    @execute_if_alive
    def exposed_send_peers(self, peer_store):
        for peer_id in list(peer_store):
            port = peer_store[peer_id]
            conn = connect('localhost', port)
            conn.root.conn_request(self.peer_id, self.port, self.connect_prob)
            conn.close()

    @execute_if_alive
    def exposed_conn_request(self, peer_id, port, connect_prob):
        if random.random() < min(connect_prob, self.connect_prob):
            self.add_peer(peer_id, port)
            conn = connect('localhost', port)
            conn.root.conn_ack(self.peer_id, self.port)
            conn.close()

    @execute_if_alive
    def exposed_conn_ack(self, peer_id, port):
        self.add_peer(peer_id, port)

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

    async def upload(self, fname):
        fpath = os.path.join(self.storage_path, "local",
                             self.modify_fname(fname))
        if not os.path.exists(fpath):
            raise Exception("No file found")
        cid = self.hash_file(fpath)
        await self.set(cid, [self.peer_id])
        await self.set(self.peer_id, self.port)
        new_path = os.path.join(
            self.storage_path, "uploaded", self.modify_fname(fname))
        shutil.move(fpath, new_path)

    @execute_if_alive  
    def exposed_upload(self, fname):
        asyncio.run(self.upload(fname))

    # Methods for download
    def has_file(self, cid, peer_id, port):            
        upload_path = os.path.join(self.storage_path, 'uploaded')
        file_list = os.listdir(upload_path)
        for fname in file_list:
            fpath = os.path.join(upload_path, fname)
            fcid = self.hash_file(fpath)
            if fcid == cid:
                if peer_id != self.peer_id:
                    conn = connect('localhost', port)
                    remote_path = os.path.join(
                        "./storage", str(peer_id), "local", fname)
                    download(conn, remote_path, fpath)
                    conn.close()
                return True
        return False

    @execute_if_alive
    def exposed_has_file(self, cid, peer_id, port):
        return self.has_file(cid, peer_id, port)
    
    async def download(self, cid):
        if self.has_file(cid, self.peer_id, self.port):
            print("Already has file")
            return
        for peer, port in self.peers.items():
            conn = connect('localhost', port)
            if (conn.root.has_file(cid, self.peer_id, self.port)):
                print("File downloaded. CID: " + cid)
                conn.close()
                return
            conn.close()
        # assume get result will be [(node_id, ip, port)]
        result = await self.get(cid)
        for peerId in result[0]['value']:
            print(peerId)
            res = await self.get(peerId)
            port = res[0]['value']
            conn = connect("127.0.0.1", port)
            if (conn.root.has_file(cid, self.peer_id, self.port)):
                print("File downloaded. CID: " + cid)
                conn.close()
                return
            conn.close()
        print("Failed to download file")

    @execute_if_alive
    def exposed_download(self, cid):
        asyncio.run(self.download(cid))
    
    # Other methods
    def exposed_kill(self):
        self.alive = False
        self.peers = {}

    def exposed_revive(self):
        self.alive = True

if __name__ == "__main__":
    pass

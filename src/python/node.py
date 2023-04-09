import asyncio
from rpyc import Service
from rpyc import connect
from rpyc.utils.classic import download
import random
import string
import os
import hashlib
import shutil
from david.network import Server
from node_timer import PingTimer, DownloadTimer
import time
import threading

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
        self.region = config['region']
        self.timer = None
        self.timer_init = False
        self.downloading = None
        self.download_peer_list = None
        self.threads = []
        self.init_timer()

    def rpc(func):
        def wrapper(self, *args, **kwargs):
            if self.alive:
                func(self, *args, **kwargs)
        return wrapper

    def calculate_delay(self, region):
        region_1 = constants.REGIONS.index(self.region)
        region_2 = constants.REGIONS.index(region)
        return (constants.BASE_LATENCY + constants.DISTANCES[region_1][region_2] * constants.DELAY_RATE)/1000

    # Methods for pinging and adding peers
    def init_timer(self):
        if not self.timer:
            self.timer = PingTimer(self.port, False)
            self.timer_init = True

    @rpc
    def exposed_ping(self):
        conn = connect('localhost', self.bootstrap_port)
        conn.root.ping(self.region, self.peer_id, self.port)
        conn.close()

    def add_peer(self, peer_id, port):
        print(f'Peer {self.peer_id} adds peer {peer_id}')
        self.peers[peer_id] = port

    # remove dead peers
    @rpc
    def exposed_remove_peer(self, region, peer_id):
        time.sleep(self.calculate_delay(region))
        if peer_id in self.peers:
            del self.peers[peer_id]

    # Methods for connecting to peers
    @rpc
    def exposed_send_peers(self, region, peer_store):
        time.sleep(self.calculate_delay(region))
        for peer_id in list(peer_store):
            if peer_id != self.peer_id:
                port = peer_store[peer_id]
                conn = connect('localhost', port)
                conn.root.conn_request(
                    self.region, self.peer_id, self.port, self.connect_prob)
                conn.close()

    @rpc
    def exposed_conn_request(self, region, peer_id, port, connect_prob):
        time.sleep(self.calculate_delay(region))
        if random.random() < min(connect_prob, self.connect_prob):
            self.add_peer(peer_id, port)
            conn = connect('localhost', port)
            conn.root.conn_ack(self.region, self.peer_id, self.port)
            conn.close()

    @rpc
    def exposed_conn_ack(self, region, peer_id, port):
        time.sleep(self.calculate_delay(region))
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

    def kill_dht(self):
        pass

    def revive_dht(self):
        pass

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
        await self.set(cid, [(self.peer_id, self.port)])
        new_path = os.path.join(
            self.storage_path, "uploaded", self.modify_fname(fname))
        shutil.move(fpath, new_path)

    @rpc
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
                    remote_path = os.path.join(
                        "./storage", str(peer_id), "uploaded", fname)
                    shutil.copy(fpath, remote_path)
                    conn = connect('localhost', port)
                    conn._config['sync_request_timeout'] = None
                    conn.root.ack_download(cid)
                    conn.close()
                return True
        return False

    @rpc
    def exposed_has_file(self, region, cid, peer_id, port):
        time.sleep(2 * self.calculate_delay(region))
        return self.has_file(cid, peer_id, port)

    async def download(self, cid):
        if self.has_file(cid, self.peer_id, self.port):
            print("Already has file")
            return
        if self.downloading:
            print("Downloading other file")
            return
        self.downloading = cid
        result = await self.get(cid)
        # peer_list = [(100, 8000), (102, 8002)]
        peer_list = [peer for peer in result['value'] if peer[0] in self.peers]
        self.download_peer_list = peer_list
        if not peer_list:
            print("Downloading failed")
            self.downloading = None
            return
        # set download timer to prevent blocking forever
        download_timer = DownloadTimer(self.port, cid)
        for peerId, port in peer_list:
            t = threading.Thread(target=self.has_file_conn,
                                 args=(port, cid, ))
            self.threads.append(t)
            t.start()

    def has_file_conn(self, port, cid):
        conn = connect("localhost", port)
        conn._config['sync_request_timeout'] = None
        conn.root.has_file(self.region, cid, self.peer_id, self.port)
        conn.close()

    @rpc
    def exposed_ack_download(self, cid):
        if self.downloading != cid:
            print("Download done")
            return
        print(f"File downloaded. CID: {cid}")
        asyncio.run(self.set(cid, self.download_peer_list +
                    [(self.peer_id, self.port)]))
        self.downloading = None
        self.download_peer_list = None
        if self.threads:
            for t in self.threads:
                t.join()

    @rpc
    def exposed_download_over(self, cid):
        if self.downloading == cid:  # download still not complete after timer ends
            print("Downloading has failed")
            self.downloading = None
            self.download_peer_list = None
            if self.threads:
                for t in self.threads:
                    t.join()

    @rpc
    def exposed_download(self, cid):
        asyncio.run(self.download(cid))

    # Other methods
    def exposed_send_server(self, server):
        self.server = server

    def exposed_kill(self):
        self.alive = False
        self.peers = {}
        #self.kill_dht()

    def exposed_revive(self):
        self.alive = True
        #self.revive_dht()


if __name__ == "__main__":
    pass

from rpyc import Service
from rpyc.utils.server import ThreadedServer


class BootstrapNode(Service):
    def __init__(self, peer_id, port):
        print("Bootstrap node initialized")
        self.peer_id = peer_id
        self.port = port
        self.peer_store = []
        self.last_pinged = []

    def exposed_ping(self, peer_id):
        print("Received ping")
        if (peer_id not in self.peer_store):
            self.peer_store.append(peer_id)
        if (peer_id not in self.last_pinged):
            self.last_pinged.append(peer_id)


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    node = BootstrapNode(18861)
    t = ThreadedServer(node.ping_service, port=node.port)
    t.start()

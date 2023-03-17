from rpyc import Service
from rpyc.utils.server import ThreadedServer
from rpyc import connect


class Node(Service):
    def __init__(self, peer_id, port, bootstrap_port, node_type):
        print(node_type + " node initialized")
        self.peer_id = peer_id
        self.port = port
        self.bootstrap_port = bootstrap_port
        self.node_type = node_type
        self.storage_path = "./" + str(self.peer_id)
        self.dht = None  # Change later
        conn = connect('localhost', bootstrap_port)
        conn.root.ping(peer_id)

    def exposed_ping(self, peer_id):
        print("Received ping")


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    node = Node(100, 8000, 18861, "server")
    t = ThreadedServer(node, port=node.port)
    t.start()

from __future__ import annotations # for type hinting
import heapq
from operator import itemgetter
import logging

log = logging.getLogger(__name__)

class Node:
    def __init__(self, node_id, ip=None, port=None):
        """
        A David Node instance.

        Args:
            node_id (bytes): A value between 0 and 2^160
            ip (string): Optional IP address where this Node lives
            port (int): Optional port for this Node (set when IP is set)
        """
        self.id = node_id # Length should be 20 bytes for SHA1
        self.ip = ip
        self.port = port
        self.long_id = int(node_id.hex() ,16)
    
    def distance_to(self, node: Node) -> int:
        """
        Get the XOR distance between this node and another
        """
        return self.long_id ^ node.long_id

    def __iter__(self):
        """
        Enables use of Node as a tuple - i.e., tuple(node) works.
        """
        return iter([self.id, self.ip, self.port])

    def __repr__(self):
        return repr([self.long_id, self.ip, self.port])
    
    def __str__(self):
        return f'{self.ip}:{self.port}'

class NodeHeap:
    def __init__(self, node, maxsize):
        self.node = node
        self.heap = []
        self.contacted = set()
        self.maxsize = maxsize

    def get_ids(self):
        return [n.id for n in self]
    
    def remove(self, peers):
        peers = set(peers)
        if not peers:
            return
        nheap = []
        for distance, node in self.heap:
            if node.id not in peers:
                heapq.heappush(nheap, (distance, node))
        self.heap = nheap
    
    def push(self, nodes):
        # Do not add contacted nodes again can be dead and the network might not know it!
        if not isinstance(nodes, list):
            nodes = [nodes]
        
        for node in nodes:
            if node not in self and (node.id not in self.contacted):
                distance = self.node.distance_to(node)
                heapq.heappush(self.heap, (distance, node))

    def get_node(self, node_id):
        for _, node in self.heap:
            if node.id == node_id:
                return node
        return None

    def mark_contacted(self, node):
        self.contacted.add(node.id)
    
    def get_uncontacted(self):
        return [n for n in self if n.id not in self.contacted]
    
    def have_contacted_all(self):
        return len(self.get_uncontacted()) == 0

    def popleft(self):
        return heapq.heappop(self.heap)[1] if self else None

    def __len__(self):
        return min(len(self.heap), self.maxsize)
    
    def __iter__(self):
        nodes = heapq.nsmallest(self.maxsize, self.heap)
        return iter(map(itemgetter(1), nodes))

    def __contains__(self, node):
        for _, other in self.heap:
            if node.id == other.id:
                return True
        return False

if __name__ == '__main__':
    from david.utils import digest
    n1 = Node(digest(str(9000)))
    n2 = Node(digest(str(9001)))
    n3 = Node(digest(str(9002)))
    n4 = Node(digest(str(9003)))
    nh = NodeHeap(n1, 3)
    nh.push([n2, n3, n4])
    for n in nh:
        print(n.long_id)
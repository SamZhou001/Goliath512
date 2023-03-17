from __future__ import annotations # for type hinting

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
        self.kbuckets = [{} for i in range(160)]
    
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
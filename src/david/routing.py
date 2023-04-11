import math
from collections import OrderedDict
import asyncio

class RoutingTable:
    def __init__(self, protocol, ksize, node):
        self.node = node
        self.protocol = protocol
        self.ksize = ksize
        self.index_length = 160
        self.flush()
    
    def flush(self):
        # self.buckets = [KBucket(self.ksize)] * 160
        self.kbuckets = [OrderedDict() for i in range(160)]

    def get_bucket_for(self, node):
        xor_dist = self.node.long_id ^ node.long_id
        return math.floor(math.log(xor_dist, 2))

    def is_new_node(self, node):
        index = self.get_bucket_for(node)
        return not (node.id in self.kbuckets[index].keys())
    
    def add_node_to_table(self, node):
        index = self.get_bucket_for(node)
        kbucket = self.kbuckets[index]

        if node.id in kbucket:
            kbucket.move_to_end(node.id)
        else:
            if len(kbucket) < self.ksize:
                kbucket[node.id] = node
            else:
                # LRU Policy for nodes in kbucket
                lru_node = next(iter(kbucket)) # get the first node
                lru_node_addr = (lru_node.ip, lru_node.port)
                asyncio.ensure_future(self.protocol.call_ping(lru_node_addr, lru_node, node))

    def remove_node_from_table(self, node):
        index = self.get_bucket_for(node)
        kbucket = self.kbuckets[index]
        if node.id in kbucket:
            kbucket.pop(node.id)

    def move_node_to_last(self, node):
        index = self.get_bucket_for(node)
        kbucket = self.kbuckets[index]
        if node.id in kbucket:
            kbucket.move_to_end(node.id)

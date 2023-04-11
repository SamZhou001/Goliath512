import math
from collections import OrderedDict
import asyncio
import logging
import heapq
from operator import itemgetter

log = logging.getLogger(__name__)

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
        log.debug(self.get_populated_kbuckets())

    def remove_node_from_table(self, node):
        index = self.get_bucket_for(node)
        kbucket = self.kbuckets[index]
        if node.id in kbucket:
            kbucket.pop(node.id)
        log.debug(self.get_populated_kbuckets())

    def move_node_to_last(self, node):
        index = self.get_bucket_for(node)
        kbucket = self.kbuckets[index]
        if node.id in kbucket:
            kbucket.move_to_end(node.id)
        log.debug(self.get_populated_kbuckets())
    
    def find_neighbors(self, node, k=None, exclude=None):
        k = k or self.ksize
        nodes = []
        for bucket in self.kbuckets:
            for nodeid in bucket.keys():
                neighbor = bucket[nodeid]
                notexcluded = (exclude is None) or (not (neighbor.long_id == exclude.long_id))
                if neighbor.id != node.id and notexcluded: 
                    heapq.heappush(nodes, (node.distance_to(neighbor), neighbor))
        
        return list(map(itemgetter(1), heapq.nsmallest(k, nodes)))
    
    def get_populated_kbuckets(self):
        return [bucket for bucket in self.kbuckets if len(bucket.keys()) != 0]

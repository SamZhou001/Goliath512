import logging
import math

from rpcudp.protocol import RPCProtocol
from collections import OrderedDict

log = logging.getLogger(__name__)

class DavidProtocol(RPCProtocol):
    def __init__(self, source_node, storage):
        super().__init__()
        self.source_node = source_node
        self.storage = storage
        self.kbuckets = [OrderedDict() for i in range(160)]

    def update_kbucket(self, sender, nodeid):
        xor_dist = self.source_node.id ^ nodeid
        kbucket_idx = math.floor(math.log(xor_dist, 2))
        kbucket = self.buckets[kbucket_idx]
        if nodeid in kbucket:
            kbucket.move_to_end(nodeid)
        else:
            if len(kbucket) < 20:
                kbucket[nodeid] = sender
            else:
                pass
                # Invoke self.call_ping??
        
    
    def rpc_ping(self, sender, nodeid):
        self.update_kbucket(self, sender, nodeid)
        log.debug(f'got a ping request from {sender}')
        return self.source_node.id
    
    def rpc_store(self, sender, nodeid, key, value):
        self.update_kbucket(self, sender, nodeid)
        log.debug(f'got a store request from {sender}, storing {key.hex()}={value}')
        self.storage[key] = value
        return True

    def rpc_find_value(self, sender, nodeid, key):
        self.update_kbucket(self, sender, nodeid)
        log.debug(f'got a find_value request from {sender}, finding {key.hex()}')
        value = self.storage.get(key, None)
        return {'value': value}

    async def call_store(self, node_to_ask, key, value):
        address = (node_to_ask.ip, node_to_ask.port)
        result = await self.store(address, self.source_node.id, key, value)
        return result

    async def call_find_value(self, node_to_ask, key):
        address = (node_to_ask.ip, node_to_ask.port)
        result = await self.find_value(address, self.source_node.id, key)
        return result[1]
    
    async def call_ping(self, node_to_ask):
        address = (node_to_ask.ip, node_to_ask.port)
        result = await self.ping(address, self.source_node.id)
        return result
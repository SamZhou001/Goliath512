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

    async def update_kbucket(self, sender_addr, nodeid):
        xor_dist = int(self.source_node.id.hex(), 16) ^ int(nodeid.hex(), 16)
        kbucket_idx = math.floor(math.log(xor_dist, 2))
        kbucket = self.kbuckets[kbucket_idx]
        if nodeid in kbucket:
            kbucket.move_to_end(nodeid)
        else:
            if len(kbucket) < 20:
                kbucket[nodeid] = sender_addr
            else:
                lru_nodeid = next(iter(kbucket))
                lru_node_addr = kbucket[lru_nodeid]
                result = await self.call_ping(lru_node_addr[0], lru_node_addr[1], lru_nodeid, 
                                              from_update_kbucket=True)
                # result will be a tuple - first arg is a boolean indicating whether a response
                # was received, and the second argument is the response if one was received.
                if result[0]:
                    kbucket.move_to_end(lru_nodeid)
                else:
                    kbucket.pop(lru_nodeid)
                    kbucket[nodeid] = sender_addr
        log.debug(f'Updated {kbucket_idx}th kbucket to be {kbucket}')

    async def rpc_ping(self, sender, nodeid):
        log.debug(f'got a ping request from {sender}')
        await self.update_kbucket(sender, nodeid)
        return self.source_node.id
    
    async def rpc_store(self, sender, nodeid, key, value):
        log.debug(f'got a store request from {sender}, storing {key.hex()}={value}')
        await self.update_kbucket(sender, nodeid)
        self.storage[key] = value
        return True

    async def rpc_find_value(self, sender, nodeid, key):
        log.debug(f'got a find_value request from {sender}, finding {key.hex()}')
        await self.update_kbucket(sender, nodeid)
        value = self.storage.get(key, None)
        return {'value': value}

    async def call_store(self, node_to_ask, key, value):
        address = (node_to_ask.ip, node_to_ask.port)
        result = await self.store(address, self.source_node.id, key, value)
        if result[0]:
            await self.update_kbucket(address, node_to_ask.id)
        return result

    async def call_find_value(self, node_to_ask, key):
        address = (node_to_ask.ip, node_to_ask.port)
        result = await self.find_value(address, self.source_node.id, key)
        if result[0]:
            await self.update_kbucket(address, node_to_ask.id)
        return result[1]
    
    async def call_ping(self, node_to_ask_ip, node_to_ask_port, 
                        node_to_ask_id, from_update_kbucket=False):
        address = (node_to_ask_ip, node_to_ask_port)
        result = await self.ping(address, self.source_node.id)
        # Don't update kbucket if the call_ping() was invoked by an update_kbucket()
        # to avoid infinite loop of pings
        if from_update_kbucket == False and result[0]:
            await self.update_kbucket(address, node_to_ask_id)
        return result
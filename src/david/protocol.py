import logging

from rpcudp.protocol import RPCProtocol

log = logging.getLogger(__name__)

class DavidProtocol(RPCProtocol):
    def __init__(self, source_node, storage):
        super().__init__()
        self.source_node = source_node
        self.storage = storage
    
    def rpc_ping(self, sender, nodeid):
        log.debug(f'got a ping request from {sender}')
        return self.source_node.id
    
    def rpc_store(self, sender, nodeid, key, value):
        log.debug(f'got a store request from {sender}, storing {key.hex()}={value}')
        self.storage[key] = value
        return True

    def rpc_find_value(self, sender, nodeid, key):
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
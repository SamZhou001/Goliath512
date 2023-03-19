import asyncio
import random
import logging

from david.protocol import DavidProtocol
from david.node import Node
from david.utils import digest

log = logging.getLogger(__name__)

class Server:

    protocol_class = DavidProtocol

    def __init__(self, node_id=None):
        self.node = Node(node_id or digest(random.getrandbits(255)))
        self.storage = dict()
        self.transport = None
        self.protocol = None
        self.other_server_nodes = None

    def stop(self):
        if self.transport is not None:
            self.transport.close()

    def _create_protocol(self):
        return self.protocol_class(self.node, self.storage)

    async def listen(self, port, interface='0.0.0.0'):
        """
        Start the server on the given port
        """
        loop = asyncio.get_event_loop()
        listen = loop.create_datagram_endpoint(self._create_protocol,
                                               local_addr=(interface, port))
        log.info(f'Node {self.node.long_id} listening on {interface}:{port}')
        self.transport, self.protocol = await listen
    
    async def bootstrap(self, addrs):
        log.debug(f'Attempting to bootstrap node with {len(addrs)} initial contacts')
        coroutine_objects = list(map(self.bootstrap_node, addrs))
        gathered = await asyncio.gather(*coroutine_objects)
        self.other_server_nodes = [node for node in gathered if node is not None]
        return self.other_server_nodes 

    async def bootstrap_node(self, addr):
        result = await self.protocol.ping(addr, self.node.id)
        return Node(result[1], addr[0], addr[1]) if result[0] else None
    
    async def set(self, key, value):
        log.info(f'setting {key} = {value} on network')
        dkey = digest(key)
        return await self.set_digest(dkey, value)
    
    async def set_digest(self, dkey, value):
        # Simple Implementation
        # Set the k,v pair on this node and the bootstrap nodes as well
        self.storage[dkey] = value

        results = [self.protocol.call_store(n, dkey, value) for n in self.other_server_nodes]

        # return true only if at least one store call succeeded
        return any(await asyncio.gather(*results))

    async def get(self, key):
        log.info(f'Looking up key {key} from network')
        dkey = digest(key)

        # if this node has it, return it
        if self.storage.get(dkey) is not None:
            return self.storage.get(dkey)

        results = [self.protocol.call_find_value(n, dkey) for n in self.other_server_nodes]

        result = await asyncio.gather(*results)

        return result

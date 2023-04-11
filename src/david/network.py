import asyncio
import random
import logging

from david.protocol import DavidProtocol
from david.node import Node
from david.utils import digest
from david.slingshot import NodeSlingShot, ValueSlingShot

from collections import OrderedDict

log = logging.getLogger(__name__)

class Server:

    protocol_class = DavidProtocol

    def __init__(self, node_id=None, ksize=3, alpha=3):
        self.node = Node(node_id or digest(random.getrandbits(255)))
        self.ksize = ksize
        self.alpha = alpha
        self.storage = OrderedDict()
        self.transport = None
        self.protocol = None
        self.other_server_nodes = None

    def stop(self):
        if self.transport is not None:
            self.transport.close()

    def _create_protocol(self):
        return self.protocol_class(self.node, self.storage, self.ksize)

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
        nodes = [node for node in gathered if node is not None]
        slingshot = NodeSlingShot(self.protocol, self.node, nodes, self.ksize, self.alpha)
        return await slingshot.find()

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
        node = Node(dkey)

        nearest = self.protocol.router.find_neighbors(node)
        if not nearest:
            log.warning("There are no known neighbors to set key %s",
                        dkey.hex())
            return False

        slingshot = NodeSlingShot(self.protocol, node, nearest, self.ksize, self.alpha)
        nodes = await slingshot.find()

        log.info(f"setting {node.long_id} on {list(map(str, nodes))}")
        biggest = max([n.distance_to(node) for n in nodes])
        if self.node.distance_to(node) < biggest:
            self.storage[dkey] = value

        results = [self.protocol.call_store(n, dkey, value) for n in nodes]

        # return true only if at least one store call succeeded
        return any(await asyncio.gather(*results))

    async def get(self, key):
        log.info(f'Looking up key {key} from network')
        dkey = digest(key)

        # if this node has it, return it
        if self.storage.get(dkey) is not None:
            return self.storage.get(dkey)
        
        node = Node(dkey)
        nearest = self.protocol.router.find_neighbors(node)
        if not nearest:
            log.warning("There are no known neighbors to get key %s", key)
            return None
        slingshot = ValueSlingShot(self.protocol, node, nearest, self.ksize, self.alpha)
        return await slingshot.find()

    async def kill(self, addr):
        result = await self.protocol.call_kill(addr[0], addr[1])
        return result

    async def revive(self, addr):
        result = await self.protocol.call_revive(addr[0], addr[1])
        return result

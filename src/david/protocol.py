import logging
import asyncio
import time

from rpcudp.protocol import RPCProtocol

from david.node import Node
from david.routing import RoutingTable
from david.utils import digest

log = logging.getLogger(__name__)
logging.getLogger("rpcudp").setLevel(logging.CRITICAL)
logging.getLogger('asyncio').setLevel(logging.CRITICAL) 


class DavidProtocol(RPCProtocol):
    def __init__(self, source_node, storage, ksize):
        super().__init__(wait_timeout = 1)
        self.source_node = source_node
        self.storage = storage
        self.router = RoutingTable(self, ksize, source_node)
        self.alive = True
        self.ksize = ksize

    def rpc_ping(self, sender, nodeid):
        time.sleep(0.07)
        log.debug(f'got a ping request from {sender}')
        source = Node(nodeid, sender[0], sender[1])
        self.handle_if_new(source)
        return self.source_node.id
    
    def rpc_store(self, sender, nodeid, key, value):
        time.sleep(0.07)
        log.debug(f'got a store request from {sender}, storing {int(key.hex(), 16)}={value}')
        source = Node(nodeid, sender[0], sender[1])
        self.handle_if_new(source)
        self.storage[key] = value
        return True

    def rpc_find_value(self, sender, nodeid, key):
        time.sleep(0.07)
        log.debug(f'got a find_value request from {sender}, finding {int(key.hex(), 16)}')
        source = Node(nodeid, sender[0], sender[1])
        self.handle_if_new(source)
        value = self.storage.get(key, None)
        if value is None:
            return self.rpc_find_node(sender, nodeid, key)
        return {'value': value}
    
    def rpc_find_node(self, sender, sender_nodeid, key):
        time.sleep(0.07)
        log.debug(f'finding neighbors of {int(sender_nodeid.hex(), 16)} in local table')
        source = Node(sender_nodeid, sender[0], sender[1])
        self.handle_if_new(source)
        node = Node(key)
        neighbors = self.router.find_neighbors(node, exclude=source)
        return list(map(tuple, neighbors))
    
    def rpc_kill(self, sender):
        log.debug(f'got kill request from {sender}')
        self.alive=False
        return self.alive

    def rpc_revive(self, sender):
        log.debug(f'got revive request from {sender}')
        self.alive=True
        return self.alive

    async def call_ping(self, address, lru_node, new_node):
        result = await self.ping(address, self.source_node.id)
        return self.handle_call_response(result, lru_node, new_node)

    async def call_store(self, node_to_ask, key, value):
        address = (node_to_ask.ip, node_to_ask.port)
        result = await self.store(address, self.source_node.id, key, value)
        return self.handle_call_response(result, node_to_ask)

    async def call_find_node(self, node_to_ask, node_to_find):
        address = (node_to_ask.ip, node_to_ask.port)
        result = await self.find_node(address, self.source_node.id, node_to_find.id)
        return self.handle_call_response(result, node_to_ask)

    async def call_find_value(self, node_to_ask, key):
        address = (node_to_ask.ip, node_to_ask.port)
        result = await self.find_value(address, self.source_node.id, key.id)
        return self.handle_call_response(result, node_to_ask)
    
    async def call_kill(self, node_to_ask_ip, node_to_ask_port):
        address = (node_to_ask_ip, node_to_ask_port)
        result = await self.kill(address)
        return result

    async def call_revive(self, node_to_ask_ip, node_to_ask_port):
        address = (node_to_ask_ip, node_to_ask_port)
        result = await self.revive(address)
        return result
    
    def handle_if_new(self, node):
        """
        Given a new node, send it all the keys/values it should be storing,
        then add it to the routing table.

        @param node: A new node that just joined (or that we just found out
        about).

        Process:
        For each key in storage, get k closest nodes.  If newnode is closer
        than the furthest in that list, and the node for this server
        is closer than the closest in that list, then store the key/value
        on the new node (per section 2.5 of the paper)
        """
        if not self.router.is_new_node(node):
            return

        log.info(f"never seen {node} before, adding to router")
        for key, value in self.storage.items():
            keynode = Node(digest(key))
            neighbors = self.router.find_neighbors(keynode) # takes into consideration k-size set on init
            # Assume neighbors returned are sorted in closest to furthest
            if neighbors:
                last = neighbors[-1].distance_to(keynode)
                new_node_closer = node.distance_to(keynode) < last
                first = neighbors[0].distance_to(keynode)
                this_node_closest = self.source_node.distance_to(keynode) < first
            if not neighbors or (new_node_closer and this_node_closest):
                asyncio.ensure_future(self.call_store(node, key, value))

        self.router.add_node_to_table(node)
    
    def handle_call_response(self, result, node, new_node=None):
        if not result[0]:
            log.info(f"no response from {node}, removing from routing table")
            self.router.remove_node_from_table(node)
            if new_node:
                self.router.add_node_to_table(new_node)
            return result

        log.info(f"got successful response from {node}")
        if new_node:
            # got successful response, need to move the new node to last
            self.router.move_node_to_last(node)
        self.handle_if_new(node)
        return result
    
    async def _accept_request(self, msg_id, data, address):
        """
        Override _accept_request function for virtual kill and revive
        """
        funcname, _ = data

        if funcname != 'revive' and (not self.alive):
            return
        
        await RPCProtocol._accept_request(self, msg_id, data, address)

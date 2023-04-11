import logging

from david.node import Node, NodeHeap
from david.utils import gather_dict

log = logging.getLogger(__name__)

class SlingShot:
    def __init__(self, protocol, node, peers, ksize, alpha):
        self.protocol = protocol
        self.node = node
        self.ksize = ksize
        self.alpha = alpha
        self.nearest = NodeHeap(self.node, self.ksize)
        self.last_ids_crawled = []
        self.nearest.push(peers)
    
    async def _find(self, rpcmethod):
        """
        Get value of key or list of nodes.

        Args:
            rpcmethod: protocol's call_find_value or call_find_node

        Process:
        """
        count = self.alpha
        if self.nearest.get_ids() == self.last_ids_crawled:
            count = len(self.nearest)
        self.last_ids_crawled = self.nearest.get_ids()

        d = dict()
        for peer in self.nearest.get_uncontacted()[:count]:
            d[peer.id] = rpcmethod(peer, self.node)
            self.nearest.mark_contacted(peer)
        found = await gather_dict(d)
        return await self._nodes_found(found)
    
    async def _nodes_found(self, responses):
        raise NotImplementedError


class NodeSlingShot(SlingShot):
    async def find(self):
        return await self._find(self.protocol.call_find_node)
    
    async def _nodes_found(self, responses):
        toremove = []
        for peerid, response in responses.items():
            response = RPCFindResponse(response)
            if not response.happened():
                toremove.append(peerid)
            else:
                self.nearest.push(response.get_node_list())
        self.nearest.remove(toremove)

        if self.nearest.have_contacted_all():
            return list(self.nearest)
        return await self.find()
    
class RPCFindResponse:
    def __init__(self, response):
        """
        A wrapper for the result of a RPC find.

        Args:
            response: This will be a tuple of (<response received>, <value>)
                      where <value> will be a list of tuples if not found or
                      a dictionary of {'value': v} where v is the value desired
        """
        self.response = response

    def happened(self):
        """
        Did the other host actually respond?
        """
        return self.response[0]

    def has_value(self):
        return isinstance(self.response[1], dict)

    def get_value(self):
        return self.response[1]['value']

    def get_node_list(self):
        """
        Get the node list in the response.  If there's no value, this should
        be set.
        """
        nodelist = self.response[1] or []
        return [Node(*nodeple) for nodeple in nodelist]
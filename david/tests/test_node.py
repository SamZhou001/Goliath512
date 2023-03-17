import random
import hashlib

from david.node import Node

class TestNode:
    def test_long_id(self):
        rid = hashlib.sha1(str(random.getrandbits(255)).encode()).digest()
        node = Node(rid)
        assert node.long_id == int(rid.hex(), 16)

    def test_distance_calculation(self):
        rid1 = hashlib.sha1(str(random.getrandbits(255)).encode())
        rid2 = hashlib.sha1(str(random.getrandbits(255)).encode())

        shouldbe = int(rid1.hexdigest(), 16) ^ int(rid2.hexdigest(), 16)
        n1 = Node(rid1.digest())
        n2 = Node(rid2.digest())
        assert n1.distance_to(n2) == shouldbe

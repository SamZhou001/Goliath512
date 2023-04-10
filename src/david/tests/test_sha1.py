from pprint import pprint
from david.utils import digest
import heapq

def generate_constant_sha1(num):
    BASE = 9000
    return [(digest(str(i)), i) for i in range(BASE, BASE+num)]

def convert_to_long_id(id):
    return int(id.hex(), 16)

def get_k_closest_nodes(key, nodes, k):
    long_id_key = int(digest(key).hex(), 16)
    heap = []

    for node in nodes:
        distance = xor_distance(long_id_key, node[0])
        heap.append((distance, node))
    
    heapq.heapify(heap)
    return heapq.nsmallest(k, heap)

def xor_distance(id1, id2):
    return id1 ^ id2

def create_rid_pairs(num):
    rids = generate_constant_sha1(6)
    return [(convert_to_long_id(rid[0]), rid[1]) for rid in rids]

def main():
    KEY = 'CS512'
    long_rids = create_rid_pairs(6)
    pprint(get_k_closest_nodes(KEY, long_rids, 3))

if __name__ == '__main__':
    main()
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
    pprint(f"Key {key} long id is {long_id_key}")
    heap = []

    for node in nodes:
        distance = xor_distance(long_id_key, node[0])
        heap.append((distance, node))
    
    heapq.heapify(heap)
    return heapq.nsmallest(k, heap)

def xor_distance(id1, id2):
    return id1 ^ id2

def create_rid_pairs(num):
    rids = generate_constant_sha1(num)
    return [(convert_to_long_id(rid[0]), rid[1]) for rid in rids]

def main():
    KEY = 'CS512'
    k = 3
    long_rids = create_rid_pairs(6)
    # pprint(long_rids)
    k_closest = get_k_closest_nodes(KEY, long_rids, k)
    generate_msg(KEY, k_closest, k)

def generate_msg(key, closest_nodes, k):
    nodes = [n[1][1] for n in closest_nodes]
    msg = f"For key {key}, {k} ports for the closest nodes are {nodes}"
    pprint(msg)


if __name__ == '__main__':
    main()
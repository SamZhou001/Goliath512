PING_TIMER = 0.5 # Time between each ping
BOOTSTRAP_PORT = 18861
SIM_INTERVAL = 1 # Amount of time between each step in network main function
HASH_DIGITS = 16 # Number of digits of each cid and dhtId
NUM_NODES = 3
NODE_CONFIG = [
    {
        "peer_id": 100 + i,
        "port": 8000 + i,
        "dht_port": 9000 + i,
        "connect_prob": 1
    }
    for i in range(NUM_NODES)
]